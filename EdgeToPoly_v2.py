"""
EdgeToPoly - Tool for converting KiCAD PCB files
This module converts PCB edges to polygon format.
"""

import sys
import argparse
from pathlib import Path
from kiutils.board import Board
import os
import uuid


# region Helper Functions
def validate_file(filepath: str) -> Path:
    """Validates file existence and type."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if path.suffix not in ['.kicad_pcb']:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return path


def order_segments_to_polygon(segments):
    """Orders segments sequentially to form a valid polygon."""
    if not segments:
        return []

    pool = list(segments)
    
    # Get first segment. Data structure: [start, arc_param, end]
    first_seg = pool.pop(0)
    ordered_edges = [first_seg]
    
    current_end_point = first_seg[2]
    
    while pool:
        found_next = False
        for i, seg in enumerate(pool):
            start, arc_param, end = seg
            
            # Case 1: Forward flow (Start matches chain end)
            if start == current_end_point:
                ordered_edges.append([start, arc_param, end])
                current_end_point = end
                pool.pop(i)
                found_next = True
                break
            
            # Case 2: Reverse flow (End matches chain end)
            elif end == current_end_point:
                ordered_edges.append([end, arc_param, start])
                current_end_point = start
                pool.pop(i)
                found_next = True
                break
        
        if not found_next:
            break
            
    return ordered_edges


def polygon_formatted_output(sorted_edges):
    """Converts sorted edges to KiCAD polygon format."""
    output = "(pts "
    previous_point = None
    
    if sorted_edges:
        start_node = sorted_edges[0][0]
        previous_point = start_node
        output += f"(xy {start_node[0]} {start_node[1]}) "

    for seg in sorted_edges:
        arc_param = seg[1]
        end_node = seg[2]
        
        if arc_param is None:
            # Straight line
            output += f"(xy {end_node[0]} {end_node[1]}) "
        else:
            # Arc
            mid_x = arc_param[0]
            mid_y = arc_param[1]
            output += f"(arc (start {previous_point[0]} {previous_point[1]}) (mid {mid_x} {mid_y}) (end {end_node[0]} {end_node[1]}) ) "

        previous_point = end_node

    output += ")"
    return output


def create_kicad_zone_entity(polygon_data: str) -> str:
    """Creates a KiCAD ZONE structure."""
    zone_uuid = str(uuid.uuid4())
    
    kicad_zone = f"""  (zone
    (net 0)
    (net_name "")
    (layers "F.Cu" "B.Cu")
    (uuid "{zone_uuid}")
    (hatch edge 0.5)
    (connect_pads
      (clearance 0.5)
    )
    (min_thickness 0.25)
    (filled_areas_thickness no)
    (fill
      (thermal_gap 0.5)
      (thermal_bridge_width 0.5)
      (island_removal_mode 1)
      (island_area_min 10)
    )
    (polygon
      {polygon_data}
    )
  )"""
    
    return kicad_zone, zone_uuid
# endregion


# region Main Functions
def append_polygon_to_file(polygon_data: str, input_filename: str, output_filename: str) -> bool:
    """
    Appends polygon data to KiCAD PCB file as ZONE.
    
    Args:
        polygon_data (str): Polygon data in (pts ...) format
        input_filename (str): Source KiCAD PCB file
        output_filename (str): Output file path
    
    Returns:
        bool: True if successful
    """
    
    if not os.path.exists(input_filename):
        print(f"✗ Error: Source file '{input_filename}' not found.")
        return False

    try:
        # Read source file
        with open(input_filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create zone structure
        kicad_zone, zone_uuid = create_kicad_zone_entity(polygon_data)
        
        # Find closing parenthesis
        last_paren_index = content.rfind(')')
        
        if last_paren_index == -1:
            print("✗ Error: Source file format is invalid.")
            return False

        # Merge new content
        new_content = content[:last_paren_index] + "\n" + kicad_zone + "\n" + content[last_paren_index:]

        # Save output file
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            f_out.write(new_content)
            
        print(f"✓ Operation successful")
        print(f"  UUID: {zone_uuid}")
        print(f"  Saved: {output_filename}")
        
        return True

    except Exception as e:
        print(f"✗ File processing error: {e}")
        return False


def process_edge_to_poly(input_filename: str, output_filename: str = None) -> bool:
    """
    Converts PCB edges to polygon format.
    
    Args:
        input_filename (str): Input KiCAD PCB file
        output_filename (str): Output file (optional)
    
    Returns:
        bool: True if successful
    """
    try:
        filepath = validate_file(input_filename)
        print(f"Processing: {filepath}")
        
        # Read KiCAD file
        board = Board.from_file(filepath)

        # Collect all segments from Edge.Cuts layer
        edge_cut_segments = []
        for item in board.graphicItems:
            if getattr(item, "layer", None) != "Edge.Cuts":
                continue

            start = [item.start.X, item.start.Y]
            middle = [item.mid.X, item.mid.Y] if hasattr(item, 'mid') else None
            end = [item.end.X, item.end.Y]

            edge_cut_segments.append([start, middle, end])
        
        if not edge_cut_segments:
            print("⚠ Warning: No segments found in Edge.Cuts layer.")
            return False
        
        # Sort and format segments
        sorted_edges = order_segments_to_polygon(edge_cut_segments)
        polygon_data = polygon_formatted_output(sorted_edges)

        # Determine output filename
        if output_filename is None:
            base, ext = os.path.splitext(filepath)
            output_filename = f"{base}_edited{ext}"

        # Append polygon to file
        success = append_polygon_to_file(polygon_data, str(filepath), output_filename)
        
        return success

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return False
# endregion


def main():
    """Command-line interface and main program flow."""
    parser = argparse.ArgumentParser(
        description="Converts KiCAD PCB edges to polygon format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python EdgeToPoly_v2.py input.kicad_pcb
  python EdgeToPoly_v2.py input.kicad_pcb -o output.kicad_pcb
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input KiCAD PCB file (.kicad_pcb)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: input_edited.kicad_pcb)',
        default=None
    )
    
    args = parser.parse_args()
    
    success = process_edge_to_poly(args.input_file, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

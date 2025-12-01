from mouse_controller import perform_click_sequence, load_box_map_from_json

# Load the box mapping from FastSAM output
box_map = load_box_map_from_json("outputs/box_mapping.json")

# Define click sequence (element IDs from the annotated image)
click_order = [61, 35, 27]

# Execute the sequence
perform_click_sequence(click_order, box_map)

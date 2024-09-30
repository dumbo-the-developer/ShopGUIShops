from flask import Flask, request, render_template, redirect
import yaml
import os

app = Flask(__name__)

# Function to read items from a YAML file
def read_items_from_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to rearrange items into specified slots
def rearrange_items(items, slot_ranges):
    new_items = {}
    current_page = 1  # Start from page 1
    sorted_items = sorted(items.items(), key=lambda x: int(x[0]))

    # Prepare a list of available slots from the given ranges
    available_slots = []
    for slot_range in slot_ranges:
        available_slots.extend(slot_range)

    for item_id, item in sorted_items:
        if not available_slots:  # If there are no available slots left
            available_slots = []  # Reset available slots for the next page
            current_page += 1  # Move to the next page
            for slot_range in slot_ranges:
                available_slots.extend(slot_range)  # Refill available slots from ranges

        if available_slots:  # Ensure we have available slots to assign
            current_slot = available_slots.pop(0)  # Get the next available slot
            item['slot'] = current_slot
            item['page'] = current_page
            new_items[item_id] = item

    return new_items

# Function to parse slot ranges from user input
def parse_slot_ranges(slot_ranges_input):
    slot_ranges = []
    for range_str in slot_ranges_input.split(','):
        start, end = map(int, range_str.split('-'))
        slot_ranges.append(list(range(start, end + 1)))
    return slot_ranges

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    data_key = request.form['data_key']
    slot_ranges_input = request.form['slot_ranges']

    if file and (file.filename.endswith('.yaml') or file.filename.endswith('.yml')):
        # Save the uploaded file temporarily
        temp_file_path = os.path.join('uploads', file.filename)
        file.save(temp_file_path)

        # Process the uploaded YAML file
        data = read_items_from_yaml(temp_file_path)
        items = data.get(data_key, {}).get('items', {})
        slot_ranges = parse_slot_ranges(slot_ranges_input)  # Parse custom slot ranges
        updated_items = rearrange_items(items, slot_ranges)

        # Update the blocks structure with rearranged items
        data[data_key]['items'] = updated_items

        # Render the updated data in a new template
        updated_yaml = yaml.dump(data, sort_keys=False)
        return render_template('result.html', updated_yaml=updated_yaml)

    return 'Invalid file format. Please upload a .yaml or .yml file.'

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=True)


import os


def get_gun_label(yaml_path):
    with open(yaml_path, 'r') as file:
        data = file.readlines()

    names = [line.split(': ')[1] for line in data if line.startswith('names')][0]
    # convert names to list
    names = [name[1:-1].lower() for name in names[1:-2].split(', ')]

    try:
        gun_label = names.index('gun')
    except ValueError:
        gun_label = names.index('0')
    return gun_label


def new_yaml(old_yaml):
    with open(old_yaml, 'r') as file:
        data = file.readlines()

    nc_idx = [i for i, line in enumerate(data) if line.startswith('nc')][0]
    data[nc_idx] = 'nc: 1\n'

    names_idx = [i for i, line in enumerate(data) if line.startswith('names')][0]
    data[names_idx] = 'names: [gun]\n'

    return data


def read_gun_only_labels(path, gun_label):
    for file in os.listdir(path):
        if file.endswith('.txt'):
            with open(os.path.join(path, file), 'r') as labels_file:
                data = labels_file.readlines()

            data = [line for line in data if int(line.split(' ')[0]) == gun_label]
            # label numbers are 0-indexed since there is only one class
            data = [f'0 {line[2:]}' for line in data]

            if data:
                yield file[:-4], data


def write_labels(path, data):
    for file, labels in data:
        with open(os.path.join(path, file + '.txt'), 'w') as labels_file:
            for label in labels:
                labels_file.write(label)


def copy_image(source_path, destination_path, file):
    filename = file + '.jpg'
    source = os.path.join(source_path, filename)
    destination = os.path.join(destination_path, filename)
    os.system(f'cp {source} {destination}')


def guns_folder(source_folder, destination_folder, gun_label):
    os.mkdir(destination_folder)

    for file, labels in read_gun_only_labels(source_folder, gun_label):
        copy_image(source_folder, destination_folder, file)
        write_labels(destination_folder, [(file, labels)])


def gun_only_dataset(source_ds, destination_ds):
    yaml_path = os.path.join(source_ds, 'data.yaml')
    gun_label = get_gun_label(yaml_path)

    new_yaml_data = new_yaml(yaml_path)
    new_yaml_path = os.path.join(destination_ds, 'data.yaml')
    with open(new_yaml_path, 'w') as file:
        file.writelines(new_yaml_data)

    # walk through the source dataset to find and copy gun-only images and labels within test, train and val folders
    for folder in ['test', 'train', 'valid']:
        # check if folder exists
        if not os.path.exists(os.path.join(source_ds, folder)):
            continue
        source_folder = os.path.join(source_ds, folder)
        destination_folder = os.path.join(destination_ds, folder)

        source_images = os.path.join(source_folder, 'images')
        source_labels = os.path.join(source_folder, 'labels')
        destination_images = os.path.join(destination_folder, 'images')
        destination_labels = os.path.join(destination_folder, 'labels')

        # create folders
        if not os.path.exists(destination_folder):
            os.mkdir(destination_folder)
        if not os.path.exists(destination_images):
            os.mkdir(destination_images)
        if not os.path.exists(destination_labels):
            os.mkdir(destination_labels)

        for file, data in read_gun_only_labels(source_labels, gun_label):
            copy_image(source_images, destination_images, file)
            write_labels(destination_labels, [[file, data]])


if __name__ == '__main__':
    for dataset in os.listdir('source_datasets'):
        source = os.path.join('source_datasets', dataset)
        destination = os.path.join('result_datasets', dataset)

        # create destination folder, if it doesn't exist
        if not os.path.exists(destination):
            os.mkdir(destination)

        gun_only_dataset(source, destination)

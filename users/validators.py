from django.core.exceptions import ValidationError

def validate_image_size(file):
    max_file_mb = 2
    if file.size > max_file_mb * 1000000:
        raise ValidationError(f'Cannot upload image larger than {max_file_mb} MB!')

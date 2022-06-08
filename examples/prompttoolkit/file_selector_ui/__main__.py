from . import FileSelector

print('please select a file: ')
result = FileSelector(selection_validator=lambda p: p.suffix == '.mp4' or True).start()
input(f'you choose "{result}"!')

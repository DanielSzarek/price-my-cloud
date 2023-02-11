def handle_uploaded_file(file):
    with open("some/file/name.txt", "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

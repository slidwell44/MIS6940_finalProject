import requests


def change_overlay_caller(file1, file2):
    try:
        fp1 = ("file1", open(file1, 'rb'))
        fp2 = ("file2", open(file2, 'rb'))

        x = requests.post("http://wimesprodsrv:8000/PDF_Overlay/", files={"file1": fp1, "file2": fp2}, stream=True)

        # print(x.status_code)
        return x.content
    except Exception as e:
        return None


if __name__ == '__main__':
    change_overlay_caller(r"C:\Users\EH3718\PycharmProjects\ComparisonOverlays\pdfs\117947_D_dwg1.pdf",
                          r"C:\Users\EH3718\PycharmProjects\ComparisonOverlays\pdfs\117947_E_dwg1.pdf")


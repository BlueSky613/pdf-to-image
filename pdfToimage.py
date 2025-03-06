from cv2 import imread, cvtColor, COLOR_BGR2HSV, inRange, bitwise_or
from pytesseract import pytesseract, image_to_string, image_to_data, Output
from csv import writer as csvWriter
from numpy import array
from fitz import open as fitzOpen, Matrix

pdffile = "Test_Redline1.pdf"
pdf = fitzOpen(pdffile)
pytesseract.tesseract_cmd = r'C:\Users\kk\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
for page_number in range(len(pdf)):
    page = pdf.load_page(page_number)
    mat = Matrix(3, 3)
    pix = page.get_pixmap(matrix=mat)
    output_image_path = f"page_{page_number + 1}.png"
    pix.save(output_image_path)
    image = imread(output_image_path)
    hsv_image = cvtColor(image, COLOR_BGR2HSV)
    lower_red1 = array([0, 100, 100])
    upper_red1 = array([10, 255, 255])
    lower_red2 = array([160, 100, 100])
    upper_red2 = array([180, 255, 255])
    mask1 = inRange(hsv_image, lower_red1, upper_red1)
    mask2 = inRange(hsv_image, lower_red2, upper_red2)
    red_mask = bitwise_or(mask1, mask2)
    custom_config = r'--oem 3 --psm 6'
    text = image_to_string(red_mask, config=custom_config)
    target_sentence = text.split('\n')
    img_height, img_width, channels = image.shape
    data = image_to_data(red_mask, output_type=Output.DICT)
    for j in range(len(target_sentence)):
        if target_sentence[j] != "":
            words = target_sentence[j].split()
            print(words)
            coordinates = []
            for i in range(len(data['text'])):
                if data['text'][i].lower() == words[0].lower():
                    if data['text'][i + len(words) - 1].lower() == words[len(words) - 1].lower():
                        x1 = data['left'][i]
                        y1 = data['top'][i]
                        width1 = data['width'][i]
                        height1 = data['height'][i]
                        x2 = data['left'][i + len(words) - 1]
                        y2 = data['top'][i + len(words) - 1]
                        width2 = data['width'][i + len(words) - 1]
                        height2 = data['height'][i + len(words) - 1]
                        coordinates.append((x1, y1, width1, height1, x2, y2, width2, height2))
                        break
            csv_file_path = f"{pdffile.replace('.pdf','')}.csv"
            if coordinates:
                for coord in coordinates:
                    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
                        writer = csvWriter(csv_file)
                        writer.writerow([target_sentence[j], round((coord[0] + coord[4] + coord[6])/6, 1), round((img_height-(coord[1] + coord[3]/2))/3, 1)])
            else:
                print(f"The sentence '{target_sentence}' was not found in the image.")
        else:
            continue

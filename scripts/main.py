
def main(url = "", *kwargs):
    if url == "":
        return("Введите URL.")
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
    except:
        return("Введите правильный URL.")

    letter_list = splitter(image)
    for x in range(len(letter_list)):
        for y in range(len(letter_list[x])):
            word = []
            for z in range(len(letter_list[x][y])):
                word.append(milinki(Image.fromarray(np.array(letter_list[x][y][z]).astype("uint8")), size=60))
                word[z] = word[z].reshape((120, 120))
            get_model()
            x1 = raspoznavanie(np.array(word))
            word = spellcheck(x1)
            text.append(word)
    s = ' '
    s = s.join(text)
    return s


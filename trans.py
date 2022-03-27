import os

locales = ['./Cache/MentionAndgetLinks/','./Cache/MentionAndgetTexts/','./Cache/MentionAndgetBackLinks/']
for locale in locales:
    filenames = os.listdir(locale)
    for filename in filenames:
        old = str(filename)
        c = False
        if '.' in filename:
            c = True
            filename = filename.replace('.', "~D~")
        if '\\' in filename:
            c = True
            filename = filename.replace('\\', "~R~")
        if '\"' in filename:
            c = True
            filename = filename.replace('\"', "~P~")  
        if '\'' in filename:
            c = True
            filename = filename.replace('\'', "~O~")
        if c:
            os.rename(os.path.join(locale, old), os.path.join(locale, filename))
            print(old)
            print(filename)
            print('\n')
input('clear')
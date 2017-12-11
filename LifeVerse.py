def writeFile(fname, title, author, tags, slides):
    order = []
    for tag in tags:
        if tag.lower() == "solo":
            order.append('s')
        else:
            tag_parts = tag.split(' ')
            order.append(tag_parts[0][0] + tag_parts[1])
        order = list(set(order)) #remove duplicates
    
    with open(fname, 'w') as f:
        f.write("<!DOCTYPE life-verse-markup-language-0.1/>\n")
        f.write("<title>" + title + "</title>\n")
        f.write("<author>" + author + "</author>\n")
        f.write("\n")
        f.write("<order>" + ", ".join(order) + "</order>\n")
        f.write("\n")
        for i in range(len(tags)):
            f.write("<" + tags[i] + "/>\n")
            f.write(str(slides[i]) + "\n\n")
        
        


import json
import os


def generate():
    with open('data.json', 'r') as fdata:
        data = json.load(fp=fdata)
    endcounts = {}
    container_path = './intent_train'
    ofs = ""
    for element in data:
        if element == "endcount":
            endcounts = data[element]
        else:
            class_name = element
            if not os.path.exists(os.path.join(container_path, class_name)):
                os.makedirs(os.path.join(container_path, class_name))
            count = endcounts[class_name]
            for query in data[element]:
                with open(container_path+'/'+class_name+'/'+class_name+'_'+str(count)+'.txt', 'w') as out_file:
                    out_file.write(query)
                ofs += "\n" + query
                count += 1
            endcounts[class_name] = count
            data[class_name] = []
    with open('sentences.txt', 'a') as fp:
        fp.write(ofs)
    data["endcount"] = endcounts
    with open('data.json', 'w') as fdata:
        json.dump(data, fdata)


if __name__ == "__main__":
    generate()
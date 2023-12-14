import pandas as pd
import module.essaycrawler as essaycrawler

df = pd.read_csv("../output_data/social_network_essay_data_V2.csv")
df = df[60:]
print(df)
df["author_list"] = df["author"].str.split(";")

def author_essay(df):
    for i in df:
        try:
            name = i.replace(" ","_")
            essaycrawler.main([i], 3, "tmp/"+name)
        except:
            print("failed")
df["author_list"].apply(author_essay)
# essaycrawler.main(["I-HSIEN TING"], 2, "tmp/"+"I_HSIEN_TING")

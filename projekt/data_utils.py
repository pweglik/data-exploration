import pandas as pd

def to_list(x):
    return x.split(" // ") if type(x)==str else []

def read_pathways(filename="data/pathways.csv"):
    pathways_df = pd.read_csv(filename)
    pathways_df["Reaction-List"] = pathways_df["Reaction-List"].str.split(" // ")
    pathways_df["Species"] = pathways_df["Species"].apply(to_list)
    pathways_df["In-Pathway"] = pathways_df["In-Pathway"].str.split(" // ")
    pathways_df["Super-Pathways"] = pathways_df["Super-Pathways"].str.split(" // ")
    pathways_df.set_index("Object ID", inplace=True)

    return pathways_df


def read_reactions(filename='data/reactions.csv'):
    reactions_df = pd.read_csv(filename)
    reactions_df["Left"] = reactions_df["Left"].str.split(" // ")
    reactions_df["Right"] = reactions_df["Right"].str.split(" // ")
    reactions_df["In-Pathway"] = reactions_df["In-Pathway"].str.split(" // ")
    reactions_df["Substrates"] = reactions_df["Substrates"].str.split(" // ")
    reactions_df["Enzymatic-Reaction"] = reactions_df["Enzymatic-Reaction"].str.split(" // ")
    reactions_df.set_index("Object ID", inplace=True)

    return reactions_df

        
def read_compounds(filename="data/compounds.csv"):
    compounds_df = pd.read_csv(filename)
    compounds_df.set_index("Object ID", inplace=True)

    return compounds_df
    

def get_popular_compounds():
    reactions_df = read_reactions()
    substrates_count = {}
    for substrates in reactions_df["Substrates"]:
        for substrate in substrates:
            if substrate in substrates_count:
                substrates_count[substrate] += 1
            else:
                substrates_count[substrate] = 1
                
    compound_popularity = pd.Series(substrates_count, name="Count").sort_values(ascending=False)
    return compound_popularity
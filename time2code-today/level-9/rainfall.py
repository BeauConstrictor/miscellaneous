def read_rainfall_csv(path: str) -> list[list[str]]:
    table = []
    with open(path, "r") as f:
        for l in f.readlines():
            table.append(l.strip().split(",")[:2])
    return table

def output_table_row(row: list[str], max_column_lens: list[int]):
    len_normed = [row[i].ljust(max_column_lens[i], " ") for i in range(len(max_column_lens))]
    print(f"| {" | ".join(len_normed)} |")
        
def output_table(table: list[list[str]], has_header: bool=True) -> None:
    columns = [[row[i] for row in table] for i in range(len(table[0]))]
    max_column_lens = [max([len(i) for i in column]) for column in columns] 
    spacer_string = "+" + "+".join(["-" * (max_column_lens[i] + 2) for i in range(len(max_column_lens))]) + "+"
    
    print(spacer_string)
    
    if has_header:    
        output_table_row(table[0], max_column_lens)
        print(spacer_string)
        for row in table[1:]:
            output_table_row(row, max_column_lens)
    else:
        for row in table:
            output_table_row(row, max_column_lens)
            
    print(spacer_string)

def convert_first_column_to_initials(initial_table: list[str]) -> list[str]:
    table = [initial_table[0]]
    
    for row in initial_table[1:]:
        initials = "".join([word[0].upper() for word in row[0].strip().split()])
        table.append([initials] + row[1:])
    
    return table

def main() -> None:
    table = read_rainfall_csv(".rainfall.csv")
    output_table(table)
    
    print()
    
    initials = convert_first_column_to_initials(table)
    output_table(initials)
    
if __name__ == "__main__":
    main()
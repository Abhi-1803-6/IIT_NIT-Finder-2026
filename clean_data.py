import pandas as pd
import re

def process_iit_sheet(file_path, sheet_name, gender):
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    header_indices = df_raw.index[df_raw[1] == 'Inst. Name/ No.'].tolist()
    all_blocks = []
    
    for i in range(len(header_indices)):
        h_idx = header_indices[i]
        end_idx = header_indices[i+1] - 1 if i + 1 < len(header_indices) else len(df_raw)
        
        start_idx = h_idx + 2
        df_block = df_raw.iloc[start_idx:end_idx].copy()
        df_block.columns = df_raw.iloc[h_idx]
        
        if 'Inst. Name/ No.' in df_block.columns:
            df_block.rename(columns={'Inst. Name/ No.': 'Institute'}, inplace=True)
            valid_cols = ['Institute'] + [col for col in df_block.columns if isinstance(col, str) and col not in ['Institute', 'Sl. No.', 'nan']]
            df_block = df_block.loc[:, df_block.columns.isin(valid_cols)]
            df_block.dropna(subset=['Institute'], inplace=True)
            
            df_melted = df_block.melt(id_vars=['Institute'], var_name='Branch', value_name='Rank_String')
            df_melted.dropna(subset=['Rank_String'], inplace=True)
            all_blocks.append(df_melted)
            
    df_combined = pd.concat(all_blocks, ignore_index=True)
    df_combined['Institute'] = df_combined['Institute'].apply(lambda x: re.sub(r'\s*\(\s*\d+\s*\)', '', str(x)).strip())
    
    ranks = df_combined['Rank_String'].astype(str).str.split(r'\n', expand=True)
    df_combined['Opening_Rank'] = pd.to_numeric(ranks[0], errors='coerce')
    df_combined['Closing_Rank'] = pd.to_numeric(ranks[1], errors='coerce')
    
    df_combined['Gender'] = gender
    df_combined['Type'] = 'IIT'
    df_combined.drop(columns=['Rank_String'], inplace=True)
    return df_combined

def process_nit_sheet(file_path, sheet_name, gender):
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    header_indices = df_raw.index[df_raw[1] == 'Institute'].tolist()
    all_blocks = []
    
    for i in range(len(header_indices)):
        h_idx = header_indices[i]
        end_idx = header_indices[i+1] - 1 if i + 1 < len(header_indices) else len(df_raw)
        
        # For NITs, the branch names are 1 row below the "Institute" cell
        start_idx = h_idx + 3
        df_block = df_raw.iloc[start_idx:end_idx].copy()
        
        col_names = df_raw.iloc[h_idx+1].copy()
        col_names[1] = 'Institute'
        df_block.columns = col_names
        
        if 'Institute' in df_block.columns:
            valid_cols = ['Institute'] + [col for col in df_block.columns if isinstance(col, str) and col not in ['Institute', 'nan']]
            df_block = df_block.loc[:, df_block.columns.isin(valid_cols)]
            df_block.dropna(subset=['Institute'], inplace=True)
            
            df_melted = df_block.melt(id_vars=['Institute'], var_name='Branch', value_name='Rank_String')
            df_melted.dropna(subset=['Rank_String'], inplace=True)
            all_blocks.append(df_melted)
            
    df_combined = pd.concat(all_blocks, ignore_index=True)
    df_combined['Institute'] = df_combined['Institute'].astype(str).str.strip()
    
    # Clean up NIT branch names (they contain new lines in the text)
    df_combined['Branch'] = df_combined['Branch'].str.replace(r'\n', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Split Ranks and clean trailing spaces specific to the NIT format
    ranks = df_combined['Rank_String'].astype(str).str.split(r'\n', expand=True)
    df_combined['Opening_Rank'] = pd.to_numeric(ranks[0].str.strip(), errors='coerce')
    df_combined['Closing_Rank'] = pd.to_numeric(ranks[1].str.strip(), errors='coerce')
    
    df_combined['Gender'] = gender
    df_combined['Type'] = 'NIT'
    df_combined.drop(columns=['Rank_String'], inplace=True)
    return df_combined

def main():
    iit_file = 'IIT OR-CR  2026 F.xlsx'
    nit_file = 'NIT 2026 OBC OR-CR.xlsx'
    
    print("Processing IIT Data...")
    df_iit_f = process_iit_sheet(iit_file, 'IIT 2026 Female (F)', 'Female')
    df_iit_m = process_iit_sheet(iit_file, 'IIT 2026 Male (F)', 'Male')
    
    print("Processing NIT Data...")
    # Skipping the first two sheets and explicitly calling the 3rd and 4th sheets
    df_nit_m = process_nit_sheet(nit_file, 'NIT 2026 (M)', 'Male')
    df_nit_f = process_nit_sheet(nit_file, 'NIT 2026 (F)', 'Female')
    
    # Combine everything into one master dataset
    df_final = pd.concat([df_iit_f, df_iit_m, df_nit_f, df_nit_m], ignore_index=True)
    
    # Export
    output_file = 'cleaned_all_colleges_2026.csv'
    df_final.to_csv(output_file, index=False)
    
    print(f"\nSuccess! Merged dataset created: {output_file}.")
    print(f"Total entries: {len(df_final)} (IITs: {len(df_iit_f) + len(df_iit_m)}, NITs: {len(df_nit_f) + len(df_nit_m)})")

if __name__ == "__main__":
    main()
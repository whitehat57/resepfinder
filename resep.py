import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress

def get_areas():
    url = "https://www.themealdb.com/api/json/v1/1/list.php?a=list"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [area['strArea'] for area in data['meals']]
    return []

def search_by_area(area):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?a={area}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['meals'] if data['meals'] else []
    return []

def get_recipe_details(meal_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['meals'][0] if data['meals'] else None
    return None

def search_recipe(food_name):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={food_name}"
    response = requests.get(url)
    
    if response.status_code != 200:
        console.print("[bold red]Error:[/bold red] Tidak dapat terhubung ke server.", style="red")
        return None
    
    data = response.json()
    if data['meals'] is None:
        console.print(f"[bold yellow]Tidak ditemukan resep untuk makanan:[/bold yellow] {food_name}", style="yellow")
        return None
    
    recipes = data['meals']
    return recipes

def get_ingredients(recipe):
    ingredients = []
    for i in range(1, 21):
        ingredient = recipe.get(f'strIngredient{i}')
        measure = recipe.get(f'strMeasure{i}')
        if ingredient and ingredient.strip():
            ingredients.append(f"{measure} {ingredient}".strip())
    return ingredients

def display_recipe(recipes):
    if not recipes:
        return

    with Progress() as progress:
        task = progress.add_task("[cyan]Mengambil detail resep...", total=len(recipes))
        
        for recipe in recipes:
            # Jika recipe adalah ID atau dictionary dengan idMeal
            if isinstance(recipe, str):
                recipe_id = recipe
            elif isinstance(recipe, dict) and 'idMeal' in recipe:
                recipe_id = recipe['idMeal']
            else:
                progress.advance(task)
                continue

            # Dapatkan detail lengkap resep
            detailed_recipe = get_recipe_details(recipe_id)
            if not detailed_recipe:
                progress.advance(task)
                continue
                
            table = Table(title=detailed_recipe["strMeal"], title_style="bold green", header_style="bold cyan", width=100)
            
            table.add_column("Informasi", justify="left", style="magenta", width=20)
            table.add_column("Detail", justify="left", style="white", width=80)

            table.add_row("Kategori", detailed_recipe.get("strCategory", "Tidak tersedia"))
            table.add_row("Area", detailed_recipe.get("strArea", "Tidak tersedia"))
            
            # Menampilkan bahan-bahan
            ingredients = get_ingredients(detailed_recipe)
            table.add_row("Bahan-bahan", "\n".join(ingredients) or "Tidak tersedia")
            
            # Memformat instruksi menjadi lebih rapi
            instructions = detailed_recipe.get("strInstructions", "Tidak tersedia").replace(". ", ".\n")
            table.add_row("Instruksi", instructions)
            table.add_row("Link Youtube", detailed_recipe.get("strYoutube", "Tidak tersedia"))
            
            console.print(table)
            console.print("")  # Tambah spasi antar resep
            progress.advance(task)

def main():
    console = Console()
    console.print(Panel.fit("[bold blue]Resep Makanan Finder[/bold blue]", border_style="blue"))
    
    while True:
        console.print("\n[bold cyan]Pilih metode pencarian:[/bold cyan]")
        console.print("1. Cari berdasarkan nama makanan")
        console.print("2. Cari berdasarkan area/negara")
        console.print("3. Keluar")
        
        choice = Prompt.ask("Pilihan Anda", choices=["1", "2", "3"])
        
        if choice == "1":
            food_name = Prompt.ask("\nMasukkan nama makanan yang ingin dicari")
            recipes = search_recipe(food_name)
            if recipes:
                console.print(f"\n[bold green]Ditemukan {len(recipes)} resep untuk makanan:[/bold green] {food_name}\n")
                display_recipe(recipes)
                
        elif choice == "2":
            areas = get_areas()
            console.print("\n[bold cyan]Daftar Area/Negara tersedia:[/bold cyan]")
            for i, area in enumerate(areas, 1):
                console.print(f"{i}. {area}")
            
            area_choice = Prompt.ask("\nPilih nomor area/negara", choices=[str(i) for i in range(1, len(areas) + 1)])
            selected_area = areas[int(area_choice) - 1]
            
            recipes = search_by_area(selected_area)
            if recipes:
                console.print(f"\n[bold green]Ditemukan {len(recipes)} resep dari {selected_area}[/bold green]\n")
                display_recipe(recipes)
        
        else:
            console.print("[bold yellow]Terima kasih telah menggunakan Resep Makanan Finder![/bold yellow]")
            break

if __name__ == "__main__":
    console = Console()
    main()

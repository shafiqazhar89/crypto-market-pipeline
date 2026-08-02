from rest_api_pipeline import coingecko_source

src = coingecko_source()
for name, resource in src.resources.items():
    print(name, "| selected:", resource.selected)

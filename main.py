import arcapi
import json

if __name__ == '__main__':
    for city in arcapi.CITIES:
        print(json.dumps(arcapi.get_game_centers_from_city(city), ensure_ascii=False, indent=2))
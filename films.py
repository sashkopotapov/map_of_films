import random
import folium
from geopy.geocoders import ArcGIS


def parser(path, films_year):
    '''
    (str) -> (set)
    This ffunction parses file location.txt and returns
    set of tuples with year, name and place of filmcasting
    '''
    sorted_films = set()
    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            try:
                if line.startswith('"'):
                    film_line_new = []
                    film_line = line.strip().split("\t")

                    # pop some additional inf about location in the end of line
                    if film_line[-1][-1] == ")": film_line.pop(-1)

                    # add year
                    film_name = film_line[0].split()
                    year = [eval(x) for x in film_name if x[-1] == ")" and x[0] == "("]
                    if year[0] == films_year:
                        film_line_new.append(year[0])
                        # add film name
                        film_line_new.append(film_line[0])
                        # add film place
                        film_line_new.append(film_line[-1])
                    sorted_films.add(tuple(film_line_new))
            except SyntaxError:
                pass
            except NameError:
                pass
    return sorted_films


def films_dict(films, number_of_films):
    '''
    (set) -> (dict)
    This function returns dictionaary of films with place of filmcasting as key
    and number of films, which was casted this year at this place as value
    '''
    dic = dict()
    films_list = list(films)
    try:

        for p, i in enumerate(films_list):
            if p < number_of_films:
                if i[-1] not in dic:
                    dic[i] = 1

                elif i[-1] in dic:
                    dic[i] += 1
    except KeyError:
        pass
    except IndexError:
        pass
    return dic


def location(film):
    '''
    (str) -> (list)
    This function returns longitude and latitude of the place
    >>>location('St. Petersburg, Florida, USA')
    [27.771190000000047, -82.63875999999993]
    >>>location('Buenos Aires, Federal District, Argentina')
    [19.404477, -99.14879925]
    '''

    geolocator = ArcGIS()
    loc = film
    coordinates = geolocator.geocode(loc, timeout=100)
    return [coordinates.latitude, coordinates.longitude]


year_of_films = int(input("Please, write year of films you would like to see: "))
set_of_films = parser('locations.txt', year_of_films)
print('parsing...')
number_of_films = int(input("Please, enter number of films of the chosen year to show(reccom: no more than 30): "))
films_dict = films_dict(set_of_films, number_of_films)

map = folium.Map(location=[48, 25], tiles='Stamen Toner', zoom_start=[3])

fg = folium.FeatureGroup(name="World_map")
for film in films_dict:
    print(film[-1], location(film[-1]))
    fg.add_child(folium.Marker(location=location(film[-1]),
                               popup=str(films_dict[film]) + ' films was/were casted this year here -  '
                                     + film[-1], icon=folium.Icon('cloud')))

fg_pp = folium.FeatureGroup(name="Country_films")
for film in films_dict:
    print(film[-1].split()[-1])
    fg_pp.add_child(folium.Marker(location=location(film[-1].split()[-1]), popup=film[-1].split()[-1],
                                  icon=folium.Icon(color='green', icon='cloud')))

count = folium.FeatureGroup(name="Countries")
count.add_child(folium.GeoJson(data=open('world.json', 'r', encoding='utf-8-sig').read(), style_function=lambda x:
{'fillColor': ('#%06X' % random.randint(0, 256 ** 3 - 1))}))

map.add_child(fg)
map.add_child(fg_pp)
map.add_child(count)
map.add_child(folium.LayerControl())
map.save('index.html')
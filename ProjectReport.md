# OpenStreetMap Project
## Data Wrangling with MongoDB
### David Vartanian

Map Area: Buenos Aires, Argentina

https://mapzen.com/data/metro-extracts/metro/buenos-aires_argentina/

## Problems encountered in the Map
### Street Type
I've noticed that normal street names in Argentina don't include *Calle* as part of their names, but other types do. For instance, *Avenida del Libertador* is an avenue. But, what is *Azcuénaga*? Well, it's a normal street. You can assume it because *Calle* is **always** omited.
Here some examples I've found using abbreviated street types, no matter the structure:

#### Av (Avenida - Avenue)
* 128 - Av. Hipólito Yrigoyen
* 316 - Av. 12 de Octubre
* Av. Doctor Honorio Pueyrredón
* Av. Dr: Ramos Mejía
* av 101 n 1661 san martin

#### PJE (Pasaje - Passageway)
* PJE A MAGALDI
* PJE DE LA VIA
* PJE ECHAG?E
* PJE HILARIO LAGOS
* PJE TARIJA

#### Calle (Street, type omitted in street name)
* 525
* Edison
* Escalada
* Lafinur
* Marcelo T. de Alvear

### Numbers as street names
In general, streets in Argentina are named after former militar or political leaders, as well as country names, or even dates of important events. However, some cities use only numbers as street names. Others, though, use number and name. For instance, *43* (just the number) or *Avenida 13* (an avenue), or a more complex structure, *900 - General Juan Lavalle*.

### Complexity does not mean problem
After auditing all streets contained in *way* tags I could not find any technical problem. It seems that someone else have done this job before. Instead, there were many irregularities on street names contained in *node* tags. That's why I decided to audit both *nodes* and *ways*. Although it's been quite complex to identify street types from street names due to the different existent structures.

### Street Auditing Results
Given the complexity on street names, I created this function using a mapping dictionary to update street names:

```python
def update_name(self, name):
    newname = name
    for k in self.mapping.keys():
        pattern = r'^'+k+'\.?\s'
        if re.match(pattern, name, re.IGNORECASE):
            newname = re.sub(pattern, self.mapping[k]+' ', name, re.IGNORECASE)
    return newname
```

#### Applying Street Type Cleaning
| Before | After |
|--------|-------|
|Avenda Avellaneda|Avenida Avellaneda|
|Cno. Belgrano e/ 473 bis y 474|Camino Belgrano e/ 473 bis y 474|
|Cno. Centenario y 461e|Camino Centenario y 461e|
|Ave. Scalabrini Ortíz|Avenida Scalabrini Ortíz|
|BV GDOR MARTIN RODRIGUEZ|Boulevard GDOR MARTIN RODRIGUEZ|
|Au Pres. H. Cámpora|Autopista Pres. H. Cámpora|


## Data Overview
### Basic statistical overview
The following information corresponds to the XML file *buenos-aires_argentina.osm* file downloaded from *MapZen Metro Extracts* website with size of 396MB, converted to a JSON file with size of 426MB.

#### MongoDB Import

```
➜  data git:(master) ✗ mongoimport -u openstreetmap -d openstreetmap -c buenosaires --file buenos-aires_argentina.json
Enter password:

2017-08-20T20:06:54.309+0200	connected to: localhost
2017-08-20T20:06:57.295+0200	[##......................] openstreetmap.buenosaires	47.0MB/426MB (11.0%)
2017-08-20T20:07:00.295+0200	[#####...................] openstreetmap.buenosaires	94.0MB/426MB (22.1%)
2017-08-20T20:07:03.295+0200	[########................] openstreetmap.buenosaires	148MB/426MB (34.7%)
2017-08-20T20:07:06.295+0200	[###########.............] openstreetmap.buenosaires	210MB/426MB (49.2%)
2017-08-20T20:07:09.295+0200	[##############..........] openstreetmap.buenosaires	264MB/426MB (61.9%)
2017-08-20T20:07:12.295+0200	[##################......] openstreetmap.buenosaires	322MB/426MB (75.6%)
2017-08-20T20:07:15.295+0200	[#####################...] openstreetmap.buenosaires	386MB/426MB (90.6%)
2017-08-20T20:07:17.214+0200	[########################] openstreetmap.buenosaires	426MB/426MB (100.0%)
2017-08-20T20:07:17.214+0200	imported 1891788 documents
```

#### Number of documents

```
> db.buenosaires.find().count()
1891788
```

#### Unique users
The total amount of unique users is *2677*, given by the following aggregation query:

```
> db.buenosaires.aggregate([
... {"$group": {"_id": "$created.uid"}},
... {"$group": {"_id": "unique_users", "count": {"$sum": 1}}}
... ])
{ "_id" : "unique_users", "count" : 2677 }
```

#### Number of nodes and ways
The total amount of nodes is *1553770*, and ways *337982*, given by the following aggregation query:

```
> db.buenosaires.aggregate([
... {"$match": {"$or": [{type:"node"},{type:"way"}]}},
... {"$group": {"_id": "$type", "count": {"$sum":1}}}
... ])
{ "_id" : "way", "count" : 337982 }
{ "_id" : "node", "count" : 1553770 }
```

#### Number of chosen type of nodes, like cafes, shops, etc.
Actually I wanted to know which are the most frequent *amenity* and *shop* nodes.

The following query reveals the Top 10 amenities:

```
db.buenosaires.aggregate([
... {"$match": {"$and": [{type:"node"}, {amenity: {"$ne": null}}]}},
... {"$group": {"_id": "$amenity", "count": {"$sum": 1}}},
... {"$sort": {"count": -1}},
... {"$limit": 10}
... ])
{ "_id" : "restaurant", "count" : 2841 }
{ "_id" : "pharmacy", "count" : 1557 }
{ "_id" : "school", "count" : 1182 }
{ "_id" : "bench", "count" : 1077 }
{ "_id" : "cafe", "count" : 1017 }
{ "_id" : "fast_food", "count" : 902 }
{ "_id" : "bank", "count" : 857 }
{ "_id" : "fuel", "count" : 817 }
{ "_id" : "parking", "count" : 600 }
{ "_id" : "ice_cream", "count" : 569 }
```

And this query reveals the Top 10 shops:

```
> db.buenosaires.aggregate([
... {"$match": {"$and": [{type: "node"}, {shop: {"$ne": null}}]}},
... {"$group": {"_id": "$shop", "count": {"$sum": 1}}},
... {"$sort": {"count": -1}},
... {"$limit": 10}
... ])
{ "_id" : "yes", "count" : 4302 }
{ "_id" : "clothes", "count" : 1404 }
{ "_id" : "convenience", "count" : 1123 }
{ "_id" : "supermarket", "count" : 1051 }
{ "_id" : "bakery", "count" : 783 }
{ "_id" : "butcher", "count" : 724 }
{ "_id" : "lottery", "count" : 682 }
{ "_id" : "hairdresser", "count" : 669 }
{ "_id" : "car_repair", "count" : 640 }
{ "_id" : "hardware", "count" : 541 }
```

Since the value *yes* is actually "*A shop of unspecified type*" as you can see [in TagInfo Documentation](https://taginfo.openstreetmap.org/keys/shop#values), let's try to get the shop type via amenity field:

```
> db.buenosaires.aggregate([
... {"$match": {"$and":[{type:"node"}, {shop:"yes"}]}},
... {"$project": {_id: 0, amenity: 1}},
... {"$group": {"_id": "$amenity", "count": {"$sum": 1}}}
... ])
{ "_id" : "taxi", "count" : 1 }
{ "_id" : "fuel", "count" : 41 }
{ "_id" : null, "count" : 4257 }
{ "_id" : "ice_cream", "count" : 2 }
{ "_id" : "events_venue", "count" : 1 }

```

Well, not really. There is a large amount of *shop: yes* documents without *amenity*. Let's see first whether it's worth to give a try to go further:

```
> db.buenosaires.aggregate([
... {"$match": {"$and":[{type:"node"}, {shop:"yes"}, {amenity:null, description:null, brand:null, craft:null}]}},
... {"$group": {"_id": "nodata", "count": {"$sum": 1}}}
... ])
{ "_id" : "nodata", "count" : 4227 }
```

After this result I decided not to go further looking for more information about shops with no description.


#### Top 3 contributing users

These are the most frequent users in this particular dataset:

```
> db.buenosaires.aggregate([
... {"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
... {"$sort": {"count": -1}},
... {"$limit": 3}
... ])
{ "_id" : "Souchong", "count" : 235340 }
{ "_id" : "AgusQui", "count" : 179087 }
{ "_id" : "argenos", "count" : 157879 }
```


## Additional Ideas
Street names in Argentina are complex due to omissions and the structure using only numbers, combined with names, or event dates. I spent some time creating a list to filter possible street names not referring to street types, what you can see in [audit.py](audit.py) file.

Since documents don't have a declared schema, it's common to find documents with different structure in the same collection. Running this map reduce command found [here](https://stackoverflow.com/a/2308036/3456290) in the MongoDB console, I've found 764 possible keys, filtering by documents with type *node*:

```
> mr = db.runCommand({
... "mapreduce": "buenosaires",
... "map": function() {
...   if (this.type == 'node') {
...     for (var key in this) {
...       emit(key, null);
...     }
...   }
... },
... "reduce": function(key, data) { return null; },
... "out": "buenosaires_keys"
... })
{
	"result" : "buenosaires_keys",
	"timeMillis" : 17075,
	"counts" : {
		"input" : 1891788,
		"emit" : 8260422,
		"reduce" : 115110,
		"output" : 764
	},
	"ok" : 1
}
> db[mr.result].distinct("_id")
[
	"FIXME",
	"Game_ID",
	"ISO3166-1_alpha2",
	"_description_",
	"_id",
	"abandoned",
	...
	"wifi",
	"wikidata",
	"wikipedia"
]
```

Given the large amount of possible keys, it would be a better idea to filter those documents having only basic keys [_id, type, id, pos, created]:

```
> db.buenosaires.find({"$where": "for (k in this) { if (this.type == 'node' && ['_id','type','id','pos','created'].indexOf(k)!==-1) { return false;}} return this;"}).count()
338018
```

Now I'm sure that almost 22% of *nodes* are not eligible to be classified. I conclude this because it's not possible to classify an element based on its position, creation information or id. So some further action should be taken with these documents, like encouraging contributors to add more accurate information. Although this query is quite expensive, since it runs javascript code for each element in the loop.

Since 22% of *nodes* are just points in the map without any further information, I think it would be a good idea to encourage contributing users to provide more information. 

### Gamification
I've seen the idea of *gamification* before. I support this idea and will give a reason why. I believe that *motivation* is our biggest inner engine. On the other hand, rewards produce motivation. That's what gamification does. A simple progress bar, level badges, public recognition or even some virtual/real prizes can help a lot to improve OpenStreetMap Project significantly.

### Making things easier
I would help a lot improving forms with better help texts and predictive algorithms to suggest values on certain fields. For instance, suggesting the type of amenity based on the name and location (what's the probability of this place to be a restaurant if in the same area 85% or nodes are also restaurants?). I've found that helping to fill out *amenity* and *shop* fields would help much more than other fields.

### End-users don't look for empty nodes
We all are also end-users. What do we expect when we look for something in our map application? I want to find that café where delicious muffins are sold, or ATM accepting international cards, grocery, and so on. Detailed information that would be very useful to find. So, I think this is the challenge: to guide contributing users to be helpful for end-users.

# Conclusion
After analysing, cleaning, and identifying problems and possible solutions, there is still much more to do. Not only to encourage contributing users (or end-users to become contributors) to enter more data. I think that another solution could be to generate data automatically using machine learning algorithms, the same way a *recommender system* could work, but for *nodes*, and asking contributing users to review.

class _EveilRoot(object):

    @classmethod
    def _esi(self):
        from evekit.reference import Client
        return Client.ESI.get()


class _EveilItem(_EveilRoot):

    ID_FROM_NAME_KEY = NotImplementedError

    _data_cache = {}

    def __init__(self, seed):
        if isinstance(seed, str):
            self.__id = self._id_from_name(seed)
        elif isinstance(seed, int):
            self.__id = seed
        else:
            raise TypeError(seed)

    @property
    def id_(self):
        return self.__id

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.__id == other.__id

    @property
    def name(self):
        return self._data_get('name')

    def _id_from_name(self, name):
        """
        Returns the id of the objects using ESI Search API. It makes an exact match.

        :param str name:
        :return int:
        """
        result = self._esi().Search.get_search(
            categories=[self.ID_FROM_NAME_KEY],
            search=name,
            strict=True,
        ).result()[0]
        assert len(result[self.ID_FROM_NAME_KEY]) == 1
        return result[self.ID_FROM_NAME_KEY][0]

    def _request_data(self, id_):
        """
        Virtual method.
        Must return the sub-class data for the given id_. This base class takes care of caching it and providing the
        _data() and _data_get() methods to access the data.

        :param int id_:
        :return dict:
        """
        raise NotImplementedError()

    def _data_get(self, key):
        try:
            return self._data[key]
        except KeyError as e:
            raise RuntimeError(
                'Data value not found for key "{}" on class {}. Valid keys are: "{}"'.format(
                    key,
                    self.__class__.__name__,
                    self._data.keys()
                )
            )

    @property
    def _data(self):
        if self.__id not in self._data_cache:
            self._data_cache[self.__id] = self._request_data(self.__id)
        return self._data_cache[self.__id]


class InventoryItem(_EveilItem):
    ID_FROM_NAME_KEY = 'inventory_type'

    def _request_data(self, id_):
        result = self._esi().Universe.get_universe_types_type_id(type_id=id_).result()[0]
        return result

    @property
    def type_id(self):
        return self._data_get('type_id')


class Region(_EveilItem):
    ID_FROM_NAME_KEY = 'region'

    def _request_data(self, id_):
        result = self._esi().Universe.get_universe_regions_region_id(region_id=id_).result()[0]
        return result

    @property
    def region_id(self):
        return self._data_get('region_id')

    def nearby_regions(self, distance=0):
        import networkx
        import os

        if distance == 0:
            return [self]

        regions = networkx.read_yaml(os.path.dirname(__file__) + '/regions.yaml')
        nearby = networkx.shortest_path_length(regions, self.name)
        nearby = [(j, i) for i,j in nearby.items()]
        nearby.sort()

        result = []
        for i_distance, i_region_name in nearby:
            if i_distance > distance:
                break
            result.append(i_region_name)

        return [Region(i) for i in result]


class Constellation(_EveilItem):
    ID_FROM_NAME_KEY = 'constellation'

    def _request_data(self, id_):
        result = self._esi().Universe.get_universe_constellations_constellation_id(constellation_id=id_).result()[0]
        return result

    @property
    def constellation_id(self):
        return self._data_get('constellation_id')

    @property
    def region(self):
        return Region(self._data_get('region_id'))


class System(_EveilItem):
    ID_FROM_NAME_KEY = 'solar_system'

    def _request_data(self, id_):
        result = self._esi().Universe.get_universe_systems_system_id(system_id=id_).result()[0]
        return result

    @property
    def system_id(self):
        return self._data_get('system_id')

    @property
    def constellation(self):
        return Constellation(
            self._data_get('constellation_id')
        )

    @property
    def region(self):
        return self.constellation.region

    def distance_to(self, system_seed):
        other_system = self.__class__(system_seed)

        route = self._esi().Routes.get_route_origin_destination(
            origin=self.system_id,
            destination=other_system.system_id
        ).result()[0]
        return len(route) - 1

    def nearby_regions(self, distance):
        return self.region.nearby_regions(distance)


class Location(_EveilItem):
    ID_FROM_NAME_KEY = 'location'

    def _request_data(self, id_):
        result = self._esi().Universe.get_universe_stations_station_id(station_id=id_).result()[0]
        return result

    @property
    def location_id(self):
        return self._data_get('location_id')

    @property
    def system(self):
        return System(self._data_get('system_id'))


class DateRange(object):
    @classmethod
    def days_ago(cls, days_ago):
        import datetime
        import pandas
        return pandas.date_range(
            datetime.date.today() - datetime.timedelta(days=days_ago),
            datetime.date.today()
        )


class MarketHistory(object):
    def __init__(self, days_ago):
        self.__date_range = DateRange.days_ago(days_ago)

    def download(self):
        """
        Call once to download the market-data history.
        """
        from evekit.online import Download

        Download.download_market_history_range(
            self.__date_range[0:7],
            ".",
            dict(skip_missing=True, tree=True, verbose=True)
        )

    def get_data_frame(self, item, regions):
        """
        @param InventoryItem item
        @param list(Region) region
        """
        from evekit.marketdata import MarketHistory

        result = MarketHistory.get_data_frame(
            dates=self.__date_range,
            types=[item.type_id],
            regions=[i.region_id for i in regions],
            config=dict(local_storage=".", tree=True, skip_missing=True, verbose=True)
        )
        return result


class Marketeer(_EveilRoot):

    def __init__(self, item):
        self.__item = InventoryItem(item)

    def get_prices(self, origin, distance=0, sell=True):
        from pandas import DataFrame

        regions = origin.nearby_regions(distance)

        orders = []
        for i_region in regions:
            r = self._esi().Market.get_markets_region_id_orders(
                region_id=i_region.region_id,
                type_id=self.__item.type_id,
                order_type='sell' if sell else 'buyss',
            ).result()[0]
            orders += r

        return DataFrame(orders, columns=('location_id', 'price'))

    def final_format(self, df, origin):
        result = df.assign(
          location=[str(Location(i)) for i in df['location_id']],
          system=[Location(i).system for i in df['location_id']],
        )
        result = result.assign(
          region=[i.region for i in result['system']],
          jumps=[origin.distance_to(i.system_id) for i in result['system']]
        )
        result = result.sort_values(by=['price', 'jumps'])
        result = result.style.format({'price': "{:,.2f}"})
        return result


class ShoppingList(object):
    """
    A list of item you have interest to buy. As you walk arround this list checks for good prices and
    notifies you when to stop to buy something of interest.
    """

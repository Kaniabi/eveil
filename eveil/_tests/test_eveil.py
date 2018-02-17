import eveil


def test_inventory_item():
    assert eveil.InventoryItem('Vespa I').type_id == 15508
    assert eveil.InventoryItem(15508).name == 'Vespa I'


def test_comparison():
    jita = eveil.System('Jita')
    arnon = eveil.System('Arnon')
    assert jita != arnon

    jita_by_id = eveil.System(30000142)
    assert jita == jita_by_id

    assert jita.region == jita_by_id.region
    assert jita.region != arnon.region


def test_universe():
    assert eveil.Region('The Forge').region_id == 10000002
    assert eveil.Region(10000002).name == 'The Forge'

    assert eveil.Constellation('Kimotoro').constellation_id == 20000020
    assert eveil.Constellation(20000020).name == 'Kimotoro'
    assert eveil.Constellation(20000020).region.name == 'The Forge'

    assert eveil.System(30000142).name == 'Jita'
    jita = eveil.System('Jita')
    assert jita.system_id == 30000142
    assert jita.constellation.name == 'Kimotoro'
    assert jita.region.name == 'The Forge'

    assert jita.distance_to('Hatakani') == 9
    assert [str(i) for i in eveil.System('Jita').nearby_regions(0)] == ['The Forge']

    assert eveil.Location(60005599).name == 'Itamo VIII - Moon 4 - Core Complexion Inc. Factory'
    assert eveil.Location(60005599).system.system_id == 30000119


def test_nearby_regions():
    region = eveil.Region('The Forge')

    assert [i.name for i in region.nearby_regions(0)] == [
        'The Forge',
    ]

    assert [i.name for i in region.nearby_regions(1)] == [
        'The Forge',
        'Etherium Reach',
        'Geminate',
        'Lonetrek',
        'Metropolis',
        'Sinq Laison',
        'The Citadel',
        'Vale of the Silent',
    ]

    assert {i.name for i in region.nearby_regions(2)} == {
        'Essence',
        'Etherium Reach',
        'Tribute',
        'Vale of the Silent',
        'The Bleak Lands',
        'Metropolis',
        'Malpais',
        'The Forge',
        'Molden Heath',
        'Verge Vendor',
        'Pure Blind',
        'Black Rise',
        'The Citadel',
        'Genesis',
        'Domain',
        'Insmother',
        'Great Wildlands',
        'Sinq Laison',
        'The Spire',
        'Perrigen Falls',
        'Heimatar',
        'The Kalevala Expanse',
        'Lonetrek',
        'Geminate',
        'Everyshore',
    }

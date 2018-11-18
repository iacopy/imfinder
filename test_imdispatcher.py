from imdispatcher import dispatch, dispatch_legacy


ROOT = 'test'


def test_imdispatcher_legacy():
    ret = dispatch_legacy(ROOT, 'templates')

    assert ret['lena.jpg'] == 'template_lena'
    assert ret['road_alert_rotated.jpg'] == 'template_alert_rotated'
    assert ret['road_alert.png'] == 'template_alert'
    assert len(ret) == 3


def test_imdispatcher():
    ret = dispatch(ROOT, ['template_lena', 'template_health', 'template_alert', 'template_gui'])

    assert ret['lena.jpg'] == 'test/template_lena'
    assert ret['road_alert.png'] == 'test/template_alert'
    assert ret['gui.png'] == 'test/template_gui'
    assert ret['Health_1.png'] == 'test/template_health'
    assert ret['Health_2.png'] == 'test/template_health'
    assert len(ret) == 5

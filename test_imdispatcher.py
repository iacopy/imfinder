from imdispatcher import dispatch


ROOT = 'test'


def test_imdispatcher():
    ret = dispatch(ROOT, 'templates')

    assert ret['lena.jpg'] == 'template_lena'
    assert ret['road_alert_rotated.jpg'] == 'template_alert_rotated'
    assert ret['road_alert.png'] == 'template_alert'
    assert len(ret) == 3

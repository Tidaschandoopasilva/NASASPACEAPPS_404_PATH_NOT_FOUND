def actions(public):
    return {'shortest-distance':'proceed','risk-weighted-astar':'risk','always-scout':'scout','uncertainty-threshold':'scout' if 4*public['prior']*(1-public['prior'])>.6 else 'proceed'}

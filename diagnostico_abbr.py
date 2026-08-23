import json

with open('standings.json', encoding='utf-8') as f:
    standings = json.load(f)

TEAM_ABBRS = {'ARI','ATL','BAL','BUF','CAR','CHI','CIN','CLE','DAL','DEN','DET','GB',
              'HOU','IND','JAX','KC','LAC','LAR','LV','MIA','MIN','NE','NO','NYG','NYJ',
              'PHI','PIT','SEA','SF','TB','TEN','WAS'}

en_json_no_en_html = set(standings.keys()) - TEAM_ABBRS
en_html_no_en_json = TEAM_ABBRS - set(standings.keys())

print("Códigos en tu standings.json que el HTML NO reconoce:", en_json_no_en_html or "(ninguno)")
print("Códigos que el HTML espera pero NO aparecen en tu JSON:", en_html_no_en_json or "(ninguno)")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

WORK_SCHEDULE = {
    'Пн': [(9,13,3),(14,18,3)], 'Вт': [(9,13,3),(14,18,3)],
    'Ср': [(9,13,3),(14,18,3)], 'Чт': [(9,13,3),(14,18,3)],
    'Пт': [(9,13,3),(14,18,3)], 'Сб': [(10,13,2),(14,16,2)], 'Нд': []
}
TOTAL_WORK_HOURS = sum((e-s) for d in WORK_SCHEDULE for s,e,_ in WORK_SCHEDULE[d])

SERVICES = {
    'Огляд':       (0.5, 300, 0.25),
    'Чистка':      (1.0, 800, 0.35),
    'Пломбування': (1.5,1200, 0.20),
    'Видалення':   (0.75,1000,0.15),
    'Відбілювання':(2.0,2500,0.05)
}
NAMES = list(SERVICES.keys())
PROBS = [p for _,_,p in SERVICES.values()]
STD_FACTOR = 0.1

OUTAGE_P = 0.05
OUTAGE_MIN, OUTAGE_MAX = 3, 4

class Clinic:
    def __init__(self):
        self.t = 0.0
        self.remaining = 0.0          # залишок обслуговування
        self.outage = 0.0             # залишок простою
        self.revenue = 0.0
        self.served = self.lost = 0
        self.busy = 0.0
        self.outage_total = 0.0
        self.log = []

    def _service(self):
        name = np.random.choice(NAMES, p=PROBS)
        mu, cost, _ = SERVICES[name]
        dur = max(0.1, np.random.normal(mu, mu*STD_FACTOR))
        return name, dur, cost

    def hour(self, day, h, end_shift, lam, log=False):
        self.t += 1.0
        if self.outage > 0:
            self.outage -= 1.0
            self.outage_total += 1.0
            if log: self.log.append((f'{day} {h}:00','Простій',f'залишок {self.outage:.1f}'))
            return

        # попереднє обслуговування
        if self.remaining > 0:
            adv = min(1.0, self.remaining)
            self.remaining -= adv
            self.busy += adv
        else:
            adv = 0.0
        free = 1.0 - adv

        arrivals = np.random.poisson(lam)
        processed = lost = 0
        for _ in range(arrivals):
            if free <= 0:
                lost += 1
                continue
            _, dur, cost = self._service()
            last = (h+1 == end_shift)
            if dur <= free:
                free -= dur
                self.busy += dur
                self.served += 1
                self.revenue += cost
                processed += 1
            elif not last:
                self.busy += free
                self.remaining = dur - free
                free = 0
                self.served += 1
                self.revenue += cost
                processed += 1
            else:
                lost += 1
        self.lost += lost
        if log:
            self.log.append((f'{day} {h}:00','Робота',
                             f'приб {arrivals} обсл {processed} втрач {lost}'))

# симуляція тижня роботи
def one_week(log=False):
    c = Clinic()
    for d in WORK_SCHEDULE:
        if np.random.rand() <= OUTAGE_P:
            c.outage = np.random.randint(OUTAGE_MIN, OUTAGE_MAX+1)
        for s,e,lam in WORK_SCHEDULE[d]:
            for h in range(s,e):
                c.hour(d, h, e, lam, log)
    return c

def many_runs(n=100):
    data = []
    for _ in range(n):
        c = one_week()
        data.append({
            'revenue': c.revenue,
            'served' : c.served,
            'lost'   : c.lost,
            'busy'   : c.busy,
            'outage' : c.outage_total
        })
    df = pd.DataFrame(data)
    df['util'] = df['busy']/TOTAL_WORK_HOURS*100
    return df

if __name__ == '__main__':
    N = 100
    print(f'Запуск {N} прогонів...')
    df = many_runs(N)

    # лог одного прогона
    c_log = one_week(log=True)
    print('\n --- Результати одного прогону---')
    print(pd.DataFrame(c_log.log, columns=['Час','Подія','Деталі']).head(10).to_markdown(index=False))

    # середні показники
    m = df.mean().round(2)
    print('\n--- Середні показники ---')
    print(pd.DataFrame({
        'Показник': ['Дохід, грн','Обсл., шт','Втрач., шт','Час зайн., год','Простій, год','Завантаж., %'],
        'Значення': [m.revenue, m.served, m.lost, m.busy, m.outage, m.util]
    }).to_markdown(index=False))

    # гістограми
    fig,ax = plt.subplots(1,3,figsize=(18,5))
    for i,col,colname in zip(range(3),['revenue','served','util'],['Дохід','Обсл. клієнти','Завантаженість %']):
        ax[i].hist(df[col], bins=15, edgecolor='k', color=['skyblue','lightgreen','salmon'][i])
        ax[i].set_title(f'Розподіл {colname}')
        ax[i].axvline(m[col], color='r', linestyle='--')
    plt.tight_layout()
    plt.show()
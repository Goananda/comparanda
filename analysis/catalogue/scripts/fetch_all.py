"""Download every motif page of the Berezkin & Duvakin catalogue that is not on disk yet.

usage: python3 -I fetch_all.py <pages_dir> [workers=2] [pause=1.0]
Polite: each worker waits <pause> seconds after every request (2 workers = about one request
per second in total).  Failed requests are retried up to three times.  Progress goes to
<pages_dir>/fetch_log.tsv and <pages_dir>/fetch_progress.txt; DONE is written at the end.
"""
import os, queue, re, subprocess, sys, threading, time

pages = sys.argv[1]
workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
pause = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
tag = sys.argv[4] if len(sys.argv) > 4 else ''          # 'reverse' = start from the end of the index
BASE = 'https://www.ruthenia.ru/folklore/berezkin/'

idx = open(os.path.join(pages, 'index-left.html'), 'rb').read().decode('cp1251', 'replace')
codes = list(dict.fromkeys(c.lower() for c in re.findall(r'<li><a[^>]*href="([a-z0-9_]+)\.html"', idx, re.I)))
todo = [c for c in codes if not (os.path.exists(os.path.join(pages, c + '.html')) and os.path.getsize(os.path.join(pages, c + '.html')) > 500)]
print(f'pages in index: {len(codes)}; to download: {len(todo)}', flush=True)

if tag == 'reverse':
    todo.reverse()
q = queue.Queue()
for c in todo:
    q.put((c, 0))
lock = threading.Lock()
stat = dict(ok=0, fail=0, bytes=0)
failed = []
t0 = time.time()
log = open(os.path.join(pages, 'fetch_log.tsv'), 'a', encoding='utf-8')


def work():
    while True:
        try:
            code, tries = q.get_nowait()
        except queue.Empty:
            return
        path = os.path.join(pages, code + '.html')
        if os.path.exists(path) and os.path.getsize(path) > 500:      # fetched meanwhile by another run
            continue
        t1 = time.time()
        r = subprocess.run(['curl', '-sS', '-m', '180', '-o', path + '.part' + tag, '-w', '%{http_code}', BASE + code + '.html'],
                           capture_output=True, text=True)
        http = r.stdout.strip()
        size = os.path.getsize(path + '.part' + tag) if os.path.exists(path + '.part' + tag) else 0
        good = http == '200' and size > 500
        with lock:
            log.write(f'{code}\t{http}\t{size}\t{time.time() - t1:.2f}\n'); log.flush()
            if good:
                os.replace(path + '.part' + tag, path)
                stat['ok'] += 1; stat['bytes'] += size
            else:
                if os.path.exists(path + '.part' + tag):
                    os.remove(path + '.part' + tag)
                if tries < 3:
                    q.put((code, tries + 1))
                else:
                    stat['fail'] += 1; failed.append((code, http))
            n = stat['ok'] + stat['fail']
            if n % 100 == 0 or q.empty():
                with open(os.path.join(pages, f'fetch_progress{tag}.txt'), 'w') as f:
                    f.write(f"{stat['ok']} ok, {stat['fail']} failed, {q.qsize()} left, {stat['bytes'] / 1e6:.1f} MB, {time.time() - t0:.0f} s\n")
        time.sleep(pause if good else pause + 4 * (tries + 1))


ths = [threading.Thread(target=work) for _ in range(workers)]
for t in ths:
    t.start()
for t in ths:
    t.join()
msg = f"finished: {stat['ok']} ok, {stat['fail']} failed {failed[:20]}, {stat['bytes'] / 1e6:.1f} MB, {time.time() - t0:.0f} s"
print(msg, flush=True)
open(os.path.join(pages, 'DONE' + tag), 'w').write(msg + '\n')

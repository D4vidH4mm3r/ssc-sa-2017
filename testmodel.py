import stopwatch
with stopwatch.timed() as t:
    print("Importing stuff (including GPS data) ... ", end="", flush=True)
    import random
    import tensorflow as tf
    import numpy as np
    import similarity
    import re
    import utils
print("done!", t)
datadir = utils.datadir

with stopwatch.timed() as t:
    print("Loading linked data for training ...")
    relevant = set((1845, 1850, 1860, 1880, 1885))
    def buildLinksDict(fd):
        links = {year: {} for year in relevant} # year -> (kip,løb) -> linkID
        for line in fd:
            split = [part.lower() for part in line.strip().split("|")]
            match = re.search(r"\d{4}", split[1])
            if match is None:
                continue
            year = int(match.group(0))
            if year not in relevant:
                continue
            kipløb = tuple(split[2:4])
            links[year][kipløb] = split[0]
        return links

    with (datadir / ".." / "links" / "linkede_personer.csv").open("r", encoding="latin1") as fd:
        links = buildLinksDict(fd)

    print("    ... loaded links, connecting to entries ...")
    def loadLinkData(links):
        linked_data = {} # linkID -> [(year, entry)]
        with utils.AllEntries() as dataSet:
            for _, year, entries in dataSet.getEntries():
                current_links = links[year]
                for entry in entries:
                    løb = entry.løbenr.split(",")[0]
                    pair = (entry.kipnr, løb)
                    if pair in current_links:
                        linkID = current_links[pair]
                        linked_data.setdefault(linkID, []).append((year, entry))
        return linked_data

    linked_data = loadLinkData(links)

    print("    ... deleting useless singletons ... ", end="", flush=True)
    useless = [key for key,val in linked_data.items() if len(val) == 1]
    for key in useless:
        del(linked_data[key])
print("done!", t)
print("Number of linked items remaining after filtering:", len(linked_data))

with stopwatch.timed() as t:
    print("Loading some random non-matching rows ... ", end="", flush=True)
    with utils.AllEntries() as dataSet:
        _, _, entries = next(dataSet.getEntries())
        unmatches = []
        for entry in entries:
            if random.random() < 0.2:
                unmatches.append(entry)
print("done!", t)

with stopwatch.timed() as t:
    print("Defining scoring and NN ... ", end="", flush=True)

    def get_score(a, b):
        name_scores = (similarity.string_linear(getattr(a, prop), getattr(b, prop))
                    for prop in ("fornavn", "mellemnavn", "efternavn", "initialer"))
        name_scores_alt = (similarity.string_inverse(getattr(a, prop), getattr(b, prop))
                    for prop in ("fornavn", "mellemnavn", "efternavn", "initialer"))
        geo_scores = (similarity.string_linear(a.fødested, b.fødested),
                    similarity.geo(a.fødested, b.fødested))
        job_scores = (similarity.string_linear(getattr(a, prop), getattr(b, prop))
                    for prop in ("civilstand", "position"))
        state_score = similarity.status(a.civilstand, b.civilstand)
        age_score = similarity.birthyear(a.fødeår, b.fødeår)
        return np.array((*name_scores, *name_scores_alt, *geo_scores, *job_scores, state_score, age_score))

    input_size = 14
    output_size = 2

    # input
    x = tf.placeholder(tf.float32, [None, input_size], name="x-in-data")
    # (target) output
    y_ = tf.placeholder(tf.float32, [None, output_size], name="y-out-data")

    W = tf.Variable(tf.zeros([input_size, output_size]))
    b = tf.Variable(tf.zeros([output_size]))

    # output layer
    y = tf.nn.softmax(tf.matmul(x, W) + b)


    cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
    s = tf.InteractiveSession()
    tf.global_variables_initializer().run()

    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print("done!", t)

with stopwatch.timed() as t:
    print("Training NN ... ", end="", flush=True)
    for i in range(100):
        data = []
        labels = []

        for linkID in random.sample(list(linked_data), 100):
            rows = linked_data[linkID]
            for (a_year, a), (b_year, b) in zip(rows[:-1], rows[1:]):
                data.append(get_score(a, b))
                labels.append((0, 1))

        for i in range(100):
            a, b = random.sample(unmatches, 2)
            data.append(get_score(a, b))
            labels.append((1, 0))

        x_train = np.vstack(data)
        y_train = np.vstack(labels)
        s.run(train_step, feed_dict={x: x_train, y_: y_train})
print("done!", t)
print("Accuracy for last training set was:", s.run(accuracy, feed_dict={x: x_train, y_: y_train}))

# De skulle være matches; forvent [1, 1, 1, ...]
# np.argmax(s.run(y, feed_dict={x: data[:10]}), axis=1)

# De skulle ikke; forvent [0, 0, 0, ...]
# np.argmax(s.run(y, feed_dict={x: data[-10:]}), axis=1)

initials_example = "mk"
print(f"Now going to compute match probabilities for all pairs with initials {initials_example}")

census_a = None # trailing last year
census_b = [] # "next" year
prev_year = None

with utils.AllEntries() as dataSet, open("output.csv", "w") as fd:
    for fn, year, entries in dataSet.getEntries():
        with stopwatch.timed() as t:
            print("Loading data for", year, "... ", end="", flush=True)
            for entry in entries:
                if utils.initial_block(entry.fornavn) == initials_example[0] and utils.initial_block(entry.efternavn) == initials_example[0]:
                    census_b.append(entry)
        print("done!", t)
        # TODO
        if census_a is not None:
            print(prev_year, "vs", year, "is", len(census_a), "x", len(census_b), "entries")
            with stopwatch.timed() as t:
                print("Doing all vs all match estimations ... ", end="", flush=True)
                scores = np.zeros((len(census_b), input_size))
                for entry_a in census_a:
                    for index, entry_b in enumerate(census_b):
                        scores[index] = get_score(entry_a, entry_b)
                    values = s.run(y, feed_dict={x: scores})
                    best_index = np.argmax(values[:,1])
                    best = census_b[best_index]
                    best_score = values[best_index][1]
                    fd.write("|".join((str(prev_year), entry_a.fornavn, entry_a.efternavn, entry_a.kipnr, entry_a.løbenr,
                                       str(year), best.fornavn, best.efternavn, best.kipnr, best.løbenr,
                                       str(best_score))) + "\n")
            print("done!", t)
        census_a = census_b
        census_b = []
        prev_year = year

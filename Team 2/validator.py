import math

ACTION_THRESHOLD = 1.5

# todoh
# =====
# [x] Parse the input dicts to filter out responses per taste
# [x] Adapt reviewlist to reflect that
# [x] Rewrite variance to take difference between generated and
#       surveyed values instead of variance within itself


class Validator:
    def __init__(self, _genlist, _surveylist):
        self.genlist = _genlist
        self.surveylist = _surveylist
        # self.reviewpairs = zip(self.genlist, self.surveylist)
        self.reviewpairs = dict()

        for flavour in self.genlist.keys():
            self.reviewpairs[flavour] = zip([item[flavour]
                                            for
                                            item in
                                            self.genlist],
                                            [item[flavour]
                                            for
                                            item in
                                            self.surveylist]
                                            )

    def quartile(self, quart):
        if (len(self.reviewlist) + 1) % quart == 0:
            return self.reviewlist[int((len(self.reviewlist) + 1) * quart)]
        index = (len(self.reviewlist) + 1) // quart
        return (self.reviewlist[index] + self.reviewlist[index + 1]) / 2

    def iqr(self):
        return (self.quartile(quart=0.75) -
                self.quartile(quart=0.25))

    def sign_quantifier(self):
        return -1 if ACTION_THRESHOLD < self.iqr() else 1

    def variance(self):
        '''
        Custom version of variance, based on the standard version.
        + std::mean has been replaced by ACTION_THRESHOLD
        + Difference is now between generated and surveyed responses,
            instead of intra-values
        + Final formula remains unchanged
        '''
        flavourvariance = dict()
        mean = ACTION_THRESHOLD
        for key in self.reviewpairs.keys():
            flavourvariance[key] = 0
            for genval, surval in self.reviewpairs[key]:
                flavourvariance[key] += ((genval - surval) - mean) ** 2
            flavourvariance[key] /= len(self.reviewpairs[key])
        return flavourvariance

    def sub_value(self):
        return (self.sign_quantifier() *
                self.quartile(0.75) *
                math.log(abs(ACTION_THRESHOLD - self.iqr())))

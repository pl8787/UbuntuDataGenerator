#! author: pl8787
#! coding: utf-8

import TextPreprocess

class Dialogue:
    def __init__(self, filename):
        """
        Initialize one dialogue object.
        """
        self.EOS = '__eos__' # end of one sentence
        self.EOU = '__eou__' # end of one utter
        self.AsW = ' %s '
        self.isvalid = True
        self.filename = filename

        self.clean_string = True
        self.enable_tags = False

        self.utterlist = []
        self.userlist = []
        self.timelist = []

        self.c_utterlist = []
        self.c_userlist = []

        self.p_utterlist = []

    def initialize(self):
        self._extractRawList()
        if self.isvalid:
            self._concatUtter()
            self._checkValid()
        if self.isvalid:
            self._preprocess(self.clean_string, self.enable_tags)

    def _extractRawList(self):
        """
        Extract User List, Utter List and Time List from raw file.
        """
        for line in open(self.filename):
            line = line.split('\t')
            # Check valid
            if line[0] == 'ubotu' or line[0] == 'ubottu' or line[0] == 'ubot3':
                self.isvalid = False
                return
            if len(line[3].strip())==0:
                continue
            self.utterlist.append(' '.join(line[3:]))
            self.userlist.append(line[1])
            
    def _concatUtter(self):
        """
        Concatenates consecutive utterances by the same user.
        """
        for idx, user in enumerate(self.userlist):
            if len(self.c_userlist) == 0 or user != self.c_userlist[-1]:
                self.c_userlist.append(user)
                self.c_utterlist.append(self.utterlist[idx] + self.AsW % self.EOU)
            else:
                self.c_utterlist[-1] += self.utterlist[idx] + self.AsW % self.EOU

    def _checkValid(self, max_turn = 3, percentage = 0.2, max_utter = 5): 
        """
        Checks whether we accept or reject a given conversation.
        """
        if len(self.c_utterlist) < max_turn:
            self.isvalid = False
            return False
        uniqueuser = {}
        for user in self.userlist:
            if len(user) != 0:
                if user not in uniqueuser:
                    uniqueuser[user] = 1
                else:
                    uniqueuser[user] += 1
        for user,value in uniqueuser.iteritems():
            if value < percentage * len(self.userlist) and len(self.userlist) > max_utter:
                self.isvalid = False
                return False
        return True

    def _preprocess(self, clean_string = True, enable_tags = False):
        for line in self.c_utterlist:
            self.p_utterlist.append(TextPreprocess.process_line(line, clean_string, enable_tags))

    def print_utters(self):
        return (self.AsW % self.EOS).join( [' '.join(u) for u in self.p_utterlist] ) + self.AsW % self.EOS

    def print_users(self):
        return ' '.join(self.c_userlist)

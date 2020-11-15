import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import math


def list_pow(list, pow_num=1):
    return [number ** pow_num for number in list]


class ConvertToVector:

    def __init__(self, s_words):
        self.s_words = s_words

    def convert_count_vector(self, data):
        count_vec = CountVectorizer(stop_words=self.s_words)

        count_data = count_vec.fit_transform(data)

        # pd.set_option("display.max_rows", None, "display.max_columns", None)
        # cv_dataframe = pd.DataFrame(count_data.toarray(), columns=count_vec.get_feature_names())
        # print(cv_dataframe)

        return count_data.toarray()

    def convert_tfidf_vector(self, data):
        tfidf_vec = TfidfVectorizer(stop_words=self.s_words)
        tfidf_data = tfidf_vec.fit_transform(data)
        # pd.set_option("display.max_rows", None, "display.max_columns", None)
        # tfidf_dataframe = pd.DataFrame(tfidf_data.toarray(), columns=tfidf_vec.get_feature_names())
        # print(tfidf_dataframe)

        return tfidf_data.toarray()

    def cosine_similarity(self, user_vector, dic_vector):
        vector_sum = 0
        vector_sqrt = 0

        for i in range(len(user_vector)):
            try:
                vector_sum += user_vector[i] * dic_vector[i]
                vector_sqrt = math.sqrt(sum(list_pow(user_vector, 2))) * math.sqrt(
                    sum(list_pow(dic_vector, 2)))
            except ValueError:
                vector_sum += user_vector[i] * 0

        cosine_number = vector_sum / vector_sqrt

        return cosine_number

import pandas as pd
from scipy.stats import shapiro
from scipy import stats

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_control = pd.read_excel("Datasets/ab_testing_data.xlsx", sheet_name="Control Group")
df_test = pd.read_excel("Datasets/ab_testing_data.xlsx", sheet_name="Test Group")


def outlier_thresholds(dataframe, variable, low_quantile=0.05, up_quantile=0.95):
    quantile_one = dataframe[variable].quantile(low_quantile)
    quantile_three = dataframe[variable].quantile(up_quantile)
    interquantile_range = quantile_three - quantile_one
    up_limit = quantile_three + 1.5 * interquantile_range
    low_limit = quantile_one - 1.5 * interquantile_range
    return low_limit, up_limit


low_limit_click, up_limit_click = outlier_thresholds(df_control, "Impression")
low_limit_click, up_limit_click = outlier_thresholds(df_control, "Click")
low_limit_purchase, up_limit_purchase = outlier_thresholds(df_control, "Purchase")
low_limit_earning, up_limit_earning = outlier_thresholds(df_control, "Earning")

# Değişkende herhangi bir aykırı değer olup olmadığını kontrol ediyor.
def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    # dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


column_names_to_set = ["Impression", "Click", "Purchase", "Earning"]

for variable in column_names_to_set:
    replace_with_thresholds(df_control, variable)
    replace_with_thresholds(df_test, variable)
    # 1. Bu A / B testinin hipotezini nasıl tanımlarsınız?
# H0: "Maximum Bidding" kampanyası sunulan Kontrol grubu ile "Average Bidding" kampanyası sunulan Test grubunun satın
# alma sayılarının ortalaması arasında istatistiksel anlamlı bir fark yoktur.

# H2: "Maximum Bidding" kampanyası sunulan Kontrol grubu ile "Average Bidding" kampanyası sunulan Test grubunun satın
# alma sayılarının ortalaması arasında istatistiksel anlamlı bir fark vardır.
df_control["Purchase"].mean()
df_test["Purchase"].mean()

# Varsayım Şartları: Normallik - Shapiro-Wilks Test
# H0: Örnek dağılımı ile teorik normal dağılım arasında istatistiksel olarak anlamlı bir fark yoktur! -False
# H1: Örnek dağılımı ile teorik normal dağılım arasında istatistiksel olarak anlamlı bir fark vardır! -True
# p-value 0.05 den küçük ise H0 reddedilir.
control_purchase = df_control["Purchase"]
test_purchase = df_test["Purchase"]
test_statistic_control, p_value_control = shapiro(control_purchase)
print('Test Statistic = %.4f, p-value = %.4f' % (test_statistic_control, p_value_control))

test_statistic_test, p_value_test = shapiro(test_purchase)
print('Test Statistic = %.4f, p-value = %.4f' % (test_statistic_test, p_value_test))

test_statistic, p_value = stats.ttest_ind(control_purchase, test_purchase, equal_var=True)

print('Test Statistic = %.4f, p-value = %.4f' % (test_statistic, p_value))
# Parametric Test
# Varsayım: Varyans Homojenliği
stats.levene(control_purchase, test_purchase)
# H0: karşılaştırılan gruplar eşit varyansa sahiptir. - False
# H1: karşılaştırılan gruplar eşit varyansa sahip değildir. - Ture
test_statistic, p_value = stats.ttest_ind(control_purchase, test_purchase, equal_var=True)

print('Test Statistic = %.4f, p-value = %.4f' % (test_statistic, p_value))
#p value değeri 0.05ten büyüktür h0 reddelimez
#Burada Örnek dağılımı ile teorik normal dağılım arasında istatistiksel olarak anlamlı bir fark yoktur
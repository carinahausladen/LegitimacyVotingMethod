"plotting whether legtimacy ratings differ by preference cluster. 
These results would tell us whether legitimacy ratings are truly only taking into account the input method
or whether the participant confused it with the content to vote upon."

rm(list=ls())
library('tidyverse')
library('broom')
library(ggpubr)
library(rstatix)

setwd("/Users/carinaines/Documents/GitHub/VotingMechanismsResearch/gitbook/")

color_blind_friendly <- c("#FFB000", "#D35FB7", "#005AB5", "#DC3220", "#009E73")

df_cluster <- read_csv("clustering_result2.csv")
df_legitimacy <- read_csv("df_legitimacy.csv")
df_legitimacy$short_id<-as.double(df_legitimacy$short_id)

df_cluster %>% 
  left_join(., df_legitimacy, by=c("short_id")) %>%
  drop_na()-> df

"plot boxplots of legitimacy ratings by voting method and cluster; separate panels for questions"

df %>% 
  mutate(question=recode_factor(question,
                                "Q1"="vaccine",
                                "Q2"="icu",
                                "Q3"="protection",
                                "Q4"="lockdown"), ordered=TRUE) %>%
  select(short_id, question, which_method, cluster_methods, cluster, rating_cvd ) %>%
  drop_na(which_method)%>%
  filter(cluster_methods=="GMM") %>%
  mutate(cluster=factor(cluster))%>% 
  
  ggboxplot(., 
            x = "which_method", y = "rating_cvd", 
            alpha=.4, width=.6,
            color = "cluster", ggtheme = theme_gray(),
            fill = "cluster", add="mean_ci")+
  geom_jitter(color="grey", size=.3, alpha=.3, width=.4, height=.1) + 
  xlab("") + ylab("Legitimacy Rating") +
  facet_wrap(~question)+
  theme_classic() +
  theme(legend.position = "bottom",
        text=element_text(size=12)) +
  scale_colour_manual(values = color_blind_friendly)+
  scale_fill_manual(values = color_blind_friendly) ->plot_temp
  
  ggexport(plot_temp, filename = "../clean_code/figures/legitimacy_kruskal.pdf",width = 8, height = 4)

"perform a krukal by groups; to answer whether legitimacy ratings significantly differ by group.
For convenience, I manually iterated through the alternatives. 
Neither by ttest nor by anova I find significant differencesin legitimacy ratings."


cluster_kruskal_function<-function(df_in, question_in, method_in){
  df_in %>% 
    select(short_id, question, which_method, cluster_methods, cluster, rating_cvd ) %>%
    drop_na(which_method) %>%
    filter(cluster_methods=="GMM") %>%
    filter(question==question_in) %>%
    filter(which_method==method_in) %>%
    mutate(cluster=factor(cluster)) %>%
    kruskal_test(rating_cvd ~ cluster) %>%
    pull(p)
}

mylist=list()
for (i in unique(df$question)) {
  for (j in unique(df$which_method)) {
    p<-cluster_kruskal_function(df_in=df, question_in=i, method_in=j)
    mylist <- append(mylist, c(i,j,p))
  }
}

df_temp<-as.data.frame(matrix(unlist(mylist), ncol=4)[c(3,6,9,12),])
colnames(df_temp)<-unique(df$question)
rownames(df_temp)<-unique(df$which_method)

stargazer::stargazer(df_temp,
                     title="Kruskal-Wallis Test p-values of legitimacy ratings by voting method, question, and cluster: evaluating the significance of differences among groups."
                     summary = FALSE,
                     label = "tab:kruskal_cluster",
                     out="../clean_code/tables/kruskal_cluster.tex")
  
#https://www.scribbr.com/statistics/anova-in-r/ do more posthoc with this
  
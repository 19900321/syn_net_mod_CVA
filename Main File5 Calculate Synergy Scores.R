setwd("XX/code")

library(synergyfinder)
library(readxl)
library(ggplot2)
library(tibble)
library(dplyr)
library('RColorBrewer')
#input data
mathews_screening_data<- read_excel('source_data//Experimental_Results.xlsx')

#data process
res <- ReshapeData(
  data = mathews_screening_data1,
  data_type = "inhibition",
  impute = TRUE,
  impute_method = NULL,
  noise = TRUE,
  seed = 1)
str(res)

#Drug synergy scoring
res <- CalculateSynergy(
  data = res,
  method = c("ZIP", "HSA", "Bliss", "Loewe"),
  Emin = NA,
  Emax = NA,
  correct_baseline = "non")

#diff_synergy_score_plot
drug_pairs_data = res$drug_pairs
interaction_scores = drug_pairs_data[, 12:15]
interaction_scores_transposed = t(interaction_scores)
interaction_scores_df = as.data.frame(interaction_scores_transposed)
interaction_scores_df = rownames_to_column(interaction_scores_df, var = "Drug_Pair_Type")
score_colors = brewer.pal(7, "YlOrRd")[6:3]
interaction_scores_df$Score_Label = sprintf("%.2f", interaction_scores_df$V1)
interaction_scores_df = arrange(interaction_scores_df, desc(V1))
ggplot(interaction_scores_df, aes(x = Drug_Pair_Type, y = V1, fill = Drug_Pair_Type)) +
  scale_fill_manual(values = score_colors) +
  geom_bar(stat = 'identity', width = 0.8, position = position_dodge(0.8), color = 'white') +
  geom_text(aes(label = Score_Label), size = 3.6, position = position_dodge(width = 0.7), vjust = -0.3) +
  theme_classic() +
  theme(axis.title.x = element_blank(),
        axis.title.y = element_blank())
#ggsave('Figre 6D',
#       width=5.5, height=4.5, dpi = 300)

#Visualization
#Dose-response curve
for (i in c(1, 2)){
  PlotDoseResponseCurve(
    data = res,
    plot_block = 1,
    drug_index = i,
    plot_new = FALSE,
    record_plot = FALSE
  )
}
#Two-drug combination visualization
#Heatmap
Plot2DrugHeatmap(
  data = res,
  plot_block = 1,
  drugs = c(1, 2),
  plot_value = "response",
  dynamic = FALSE,
  summary_statistic = c("mean",  "median")
)

Plot2DrugHeatmap(
  data = res,
  plot_block = 1,
  drugs = c(1, 2),
  plot_value = "ZIP_synergy",
  dynamic = FALSE,
  summary_statistic = c( "quantile_25", "quantile_75")
)

#3D surface plot
Plot2DrugSurface(
  data = res,
  plot_block = 1,
  drugs = c(1, 2),
  plot_value = "response",
  dynamic = FALSE,
  summary_statistic = c("mean", "quantile_25", "median", "quantile_75")
)
##3D ZIP Score
Plot2DrugSurface(
  data = res,
  plot_block = 1,
  drugs = c(1, 2),
  plot_value = "ZIP_synergy",
  dynamic = FALSE,
  summary_statistic = c("mean", "quantile_25", "median", "quantile_75")
)



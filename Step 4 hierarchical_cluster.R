setwd("XX/code")
getwd()

library(pheatmap)
library(showtext)
library(RColorBrewer)
library(dplyr)

font_add('Arial','/Library/Fonts/Arial.ttf') 
showtext_auto()
matrix_cluster<- read.csv('result/matrix_cluster_result_admet.csv',check.names=F)
matrix_type<- read.csv('result/matrix_type_result_admet.csv',check.names=F)


unique_values <- unique(matrix_type[, 1])
new_data <- data.frame(node = unique_values)
columns <- c("SHZKJN", "HLZKKL", "SGMHT",'SZJQT','JWDCT')
for (column in columns) {
  new_column <- paste(column)
  new_data[, new_column] <- 0
  for (i in 1:length(unique_values)) {
    has_value <- column %in% matrix_type[matrix_type[, 1] == unique_values[i], 2]
    if (has_value) {
      new_data[i, new_column] <- 1
    }
  }
}

rownames(matrix_cluster)=matrix_cluster[,1]
matrix_cluster=matrix_cluster[,-1]
annotation_col= data.frame(JWDCT=new_data$JWDCT,
                           SZJQT=new_data$SZJQT,
                           SGMHT=new_data$SGMHT,
                           HLZKKL=new_data$HLZKKL,
                           SHZKJN=new_data$SHZKJN,
                           row.names = new_data$node)

ann_colors=list(SHZKJN = c("#F7F7F7",'#41AB5D'),
                HLZKKL=c("#F7F7F7",'#41AB5D'),
                SGMHT= c("#F7F7F7",'#41AB5D'),
                SZJQT= c("#F7F7F7",'#41AB5D'),
                JWDCT= c("#F7F7F7",'#41AB5D'))

plot=pheatmap(matrix_cluster,cutree_rows = 3,
              cutree_cols = 3,
              colorRampPalette(rev(brewer.pal(11,"RdBu")[2:6]))(100),
              treeheight_col = 20,treeheight_row = 20,fontsize=14,
              annotation_col=annotation_col,
              annotation_colors = ann_colors,
              display_numbers = FALSE,
              angle_col = 45)
plot
outputFolder <- file.path( "figure")
pdf(file = file.path(outputFolder, "heatmap.pdf"), width =12, height = 10)
plot
dev.off()


#annotation
matrix_herb_type<- read.csv('result/matrix_herb_result_admet.csv',check.names=F)
matrix_data <- as.matrix(table(matrix_herb_type$herb, matrix_herb_type$ingredient) > 0)
numeric_matrix <- apply(matrix_data , c(1, 2), function(x) ifelse(x, 1, 0))
numeric_matrix <- as.data.frame(numeric_matrix)
transposed_matrix <- t(numeric_matrix)

anno=pheatmap(transposed_matrix,
              color = c("#F7F7F7", '#A6D96A'),
              treeheight_col = 20,
              treeheight_row = 20,
              fontsize = 14,
              angle_col = 90)

anno
outputFolder <- file.path( "Result")
pdf(file = file.path(outputFolder, "Figure6_annatation_cluster_ingre_fangji_heatmap.pdf"), width =4.5, height = 6)
anno
dev.off()




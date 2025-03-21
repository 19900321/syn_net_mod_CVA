setwd("XX/")
getwd()

library(ggplot2)
library(ggalluvial)
library(RColorBrewer)

ingre<-read.csv('result\\sankey_diagram_file.csv')
ingre=ingre[,c(5,3,2)]
df <- to_lodes_form(ingre[,1:ncol(ingre)],
                    axes = 1:ncol(ingre),
                    id = "value")
col<- rep (brewer.pal(10, 'Spectral')[c(2:10)],5)   
plot=ggplot(df, aes(x = x, fill=stratum, label=stratum,
                    stratum = stratum, alluvium  = value))+
  geom_flow(width = 0.3,
            curve_type = "sine",
            alpha = 0.7,
            color = 'white',
            size = 0.1)+
  geom_stratum(width = 0.28,alpha = .8, color = NA)+
  geom_text(stat = 'stratum', size =6, color = 'black')+
  scale_fill_manual(values = col)+
  theme_void()+
  theme(legend.position = 'none')
plot
outputFolder <- file.path("result", "figure")
pdf(file = file.path(outputFolder, "sankey_diagram.pdf"), width =16.5, height = 8)
plot(plot)
dev.off()

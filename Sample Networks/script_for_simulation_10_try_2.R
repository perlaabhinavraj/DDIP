library(statnet)

node_number <- 10
inpath_observed <- sprintf("~/Documents/uav_ERGM_inputs/%s_observed_uav.txt", node_number)
inpath_closeness<- sprintf("~/Documents/uav_ERGM_inputs/%s_closeness_uav.txt", node_number)
A <- matrix(scan(inpath_observed, n = node_number*node_number), node_number, node_number, byrow = TRUE)
UAVnet <- as.network.matrix(A, matrix.type = "adjacency", directed = FALSE)
att <-read.table(inpath_closeness, header = FALSE)
att <- as.vector(att)
set.vertex.attribute(UAVnet,"close",att, v = 1:node_number)

model <- ergm(UAVnet ~ density + gwesp(.45, fixed = T) + degree(3:4) +kstar(2)  +smalldiff("close",2))
summary(model)
model.gof <- gof(model ~ degree + esp + distance, nsim = 10)
model.gof

testbed.simulation <- simulate(model, nsim=1000, burnin = 10000, seed = NULL)

edge_list_matrices <- vector("list", 10)
i <- 1 
while (i<= 10){
edge_list_matrices[[i]] <- as.matrix(testbed.simulation[[i]], matrix.type = "edgelist")
i <- i+1
}
base_name <- sprintf("~/Documents/uav_ergm_samples/%s_nodes", node_number)
i <- 1 
while (i <= 10){
	print(edge_list_matrices[[i]][,])
	outpath <- sprintf("%s/%s_uav_sample_graph_density_%s.txt",base_name,node_number,i)
	write.table(edge_list_matrices[[i]][,],file = outpath, col.names = FALSE, row.names = FALSE)
	i <- i + 1 
}


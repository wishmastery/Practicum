#include <iostream>
#include "neuralNetwork.h"
#include "neuralNetworkTrainer.h"
using namespace std;

int main()
{
    //create data set reader and load data file
    dataReader d;
    d.loadDataFile("data_normalized.csv",16,1);
    d.setCreationApproach( STATIC, 10);
    
    //create neural network
    neuralNetwork nn(16,16,1);
    
    //create neural network trainer
    neuralNetworkTrainer nT( &nn );
    nT.setTrainingParameters(0.01, 0.9, false);
    nT.setStoppingConditions(1000, 99);
    nT.enableLogging("log.csv", 1);
    
    //train neural network on data sets
    for (int i=0; i < d.getNumTrainingSets(); i++ ){
        nT.trainNetwork( d.getTrainingDataSet() );
    }
    
    //save the weights
    string name = "weights.csv";
    nn.saveWeights(&name[0u]);

    cout << endl << endl << "-- END OF PROGRAM --" << endl;
    return 0;
}


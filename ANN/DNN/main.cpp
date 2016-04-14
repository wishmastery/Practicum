//###begin<includes>
//noisy AutoencoderModel model and deep network
#include <shark/Models/FFNet.h>// neural network for supervised training
#include <shark/Models/Autoencoder.h>// the autoencoder to train unsupervised
#include <shark/Models/ImpulseNoiseModel.h>// model adding noise to the inputs
#include <shark/Models/ConcatenatedModel.h>// to concatenate Autoencoder with noise adding model
#include <shark/Models/LinearModel.h> // linear model

//training the  model
#include <shark/ObjectiveFunctions/ErrorFunction.h>//the error function performing the regularisation of the hidden neurons
#include <shark/ObjectiveFunctions/Loss/SquaredLoss.h> // squared loss used for unsupervised pre-training
#include <shark/ObjectiveFunctions/Loss/CrossEntropy.h> // loss used for supervised training
#include <shark/ObjectiveFunctions/Loss/ZeroOneLoss.h> // loss used for evaluation of performance
#include <shark/ObjectiveFunctions/Regularizer.h> //L1 and L2 regularisation
#include <shark/Algorithms/GradientDescent/CG.h> // optimizer: gradient descent
#include <shark/Algorithms/GradientDescent/SteepestDescent.h> //optimizer: simple gradient descent.
#include <shark/Algorithms/GradientDescent/Rprop.h> //optimizer for autoencoders

// data
#include <vector>
#include <shark/Data/Dataset.h>
#include <shark/Data/Csv.h>

// for input normalization
#include <shark/Models/Normalizer.h> 
#include <shark/Algorithms/Trainers/NormalizeComponentsUnitVariance.h> 
//###end<includes>

using namespace std;
using namespace shark;

LabeledData<RealVector, unsigned int> loadData(const std::string& dataFile,const std::string& labelFile){
    //we first load two separate data files for the training inputs and the labels of the data point
    Data<RealVector> inputs;
    Data<unsigned int> labels;
    try {
        importCSV(inputs, dataFile);
        importCSV(labels, labelFile);
    } catch (...) {
        cerr << "Unable to open file " <<  dataFile << " and/or " << labelFile << ". Check paths!" << endl;
        exit(EXIT_FAILURE);
    }
    //now we create a complete dataset which represents pairs of inputs and labels
    bool removeMean = true;
    Normalizer<RealVector> normalizer;
    NormalizeComponentsUnitVariance<RealVector> normalizingTrainer(removeMean);
    normalizingTrainer.train(normalizer, inputs);
    UnlabeledData<RealVector> normalizedData = transform(inputs, normalizer);
    LabeledData<RealVector, unsigned int> data(inputs, labels);
    exportCSV(inputs, "inputs.csv");
    return data;
}

//training of an auto encoder with one hidden layer
//###begin<function>
template<class AutoencoderModel>
AutoencoderModel trainAutoencoderModel(
                                       UnlabeledData<RealVector> const& data,//the data to train with
                                       std::size_t numHidden,//number of features in the AutoencoderModel
                                       double regularisation,//strength of the regularisation
                                       double noiseStrength, // strength of the added noise
                                       std::size_t iterations //number of iterations to optimize
){
    //###end<function>
    //###begin<model>
    //create the model
    std::size_t inputs = dataDimension(data);
    AutoencoderModel baseModel;
    baseModel.setStructure(inputs, numHidden);
    initRandomUniform(baseModel,-0.1*std::sqrt(1.0/inputs),0.1*std::sqrt(1.0/inputs));
    ImpulseNoiseModel noise(inputs,noiseStrength,0.0);//set an input pixel with probability p to 0
    ConcatenatedModel<RealVector,RealVector> model = noise>> baseModel;
    //###end<model>
    //###begin<objective>
    //create the objective function
    LabeledData<RealVector,RealVector> trainSet(data,data);//labels identical to inputs
    SquaredLoss<RealVector> loss;
    ErrorFunction error(trainSet, &model, &loss);
    TwoNormRegularizer regularizer(error.numberOfVariables());
    error.setRegularizer(regularisation,&regularizer);
    //###end<objective>
    //set up optimizer
    //###begin<optimizer>
    IRpropPlusFull optimizer;
    optimizer.init(error);
    std::cout<<"Optimizing model: "+model.name()<<std::endl;
    for(std::size_t i = 0; i != iterations; ++i){
        optimizer.step(error);
        std::cout<<i<<" "<<optimizer.solution().value<<std::endl;
    }
    //###end<optimizer>
    model.setParameterVector(optimizer.solution().point);
    return baseModel;
}

//###begin<network_types>
typedef Autoencoder<RectifierNeuron,LinearNeuron> AutoencoderModel;//type of autoencoder
typedef FFNet<RectifierNeuron,LinearNeuron> Network;//final supervised trained structure
//###end<network_types>

//unsupervised pre training of a network with two hidden layers
//###begin<pretraining_autoencoder>
Network unsupervisedPreTraining(
                                UnlabeledData<RealVector> const& data,
                                std::size_t numHidden1,std::size_t numHidden2, std::size_t numOutputs,
                                double regularisation, double noiseStrength, std::size_t iterations
                                ){
    //train the first hidden layer
    std::cout<<"training first layer"<<std::endl;
    AutoencoderModel layer =  trainAutoencoderModel<AutoencoderModel>(
                                                                      data,numHidden1,
                                                                      regularisation, noiseStrength,
                                                                      iterations
                                                                      );
    //compute the mapping onto the features of the first hidden layer
    UnlabeledData<RealVector> intermediateData = layer.evalLayer(0,data);
    
    //train the next layer
    std::cout<<"training second layer"<<std::endl;
    AutoencoderModel layer2 =  trainAutoencoderModel<AutoencoderModel>(
                                                                       intermediateData,numHidden2,
                                                                       regularisation, noiseStrength,
                                                                       iterations
                                                                       );
    //###end<pretraining_autoencoder>
    //###begin<pretraining_creation>
    //create the final network
    Network network;
    network.setStructure(dataDimension(data),numHidden1,numHidden2, numOutputs);
    initRandomNormal(network,0.1);
    network.setLayer(0,layer.encoderMatrix(),layer.hiddenBias());
    network.setLayer(1,layer2.encoderMatrix(),layer2.hiddenBias());
    
    return network;
    //###end<pretraining_creation>
}

//unsupervised pre training of a network with multiple hidden layers
//###begin<pretraining_autoencoder>
Network unsupervisedPreTrainingMultipleLayers(
                                UnlabeledData<RealVector> const& data,
                                std::vector<size_t> const& layers, std::size_t numOutputs,
                                double regularisation, double noiseStrength, std::size_t iterations
                                ){
    //train the first hidden layer
    vector<AutoencoderModel> layerVector;
    UnlabeledData<RealVector> intermediateData = data;
    for (size_t i = 1; i < layers.size()-1; ++i){
        std::cout<<"training layer " << i <<std::endl;
        AutoencoderModel layer =  trainAutoencoderModel<AutoencoderModel>(
                                                                          intermediateData,layers[i],
                                                                          regularisation, noiseStrength,
                                                                          iterations
                                                                          );
        layerVector.push_back(layer);
        //compute the mapping onto the features of the first hidden layer
        if (i != layers.size()-2) {
            cout << "bug below" << endl;
            intermediateData = layer.evalLayer(0,intermediateData);
        }
    }
    //###end<pretraining_autoencoder>
    //###begin<pretraining_creation>
    //create the final network
    Network network;
    network.setStructure(layers);
    initRandomNormal(network,0.1);
    for(size_t j = 0; j < layers.size()-2; ++j){
        network.setLayer(j,layerVector[j].encoderMatrix(),layerVector[j].hiddenBias());
    }
    return network;
    //###end<pretraining_creation>
}

int main()
{
    //###begin<supervised_training>
    //model parameters
    std::size_t numHidden = 45; // number of hidden neurons for each hidden layer
    std::size_t numHiddenLayer = 2; // number of hidden layers
    
    //unsupervised hyper parameters
    double unsupRegularisation = 0.01; // default 0.001
    double noiseStrength = 0.3; // default 0.3
    std::size_t unsupIterations = 1000; // default 100
    //supervised hyper parameters
    double regularisation = 0.0001; // default 0.0001
    std::size_t iterations = 1000; // default 100
    
    //load data
    LabeledData<RealVector,unsigned int> data = loadData("datalag3.csv", "labellag3.csv");
    
    // shuffle data
    data.shuffle();
    
    // split into training set and test set
    LabeledData<RealVector,unsigned int> test =splitAtElement(data,static_cast<std::size_t>(0.8*data.numberOfElements()));
    
    //set up hidden layer parameters
    vector<size_t> layer;
    layer.push_back(inputDimension(data));
    cout << "inputs: " << inputDimension(data) << " outputs: " << numberOfClasses(data)<< endl;
    for (size_t i = 0; i < numHiddenLayer; ++i){
        layer.push_back(numHidden);
    }
    layer.push_back(numberOfClasses(data));
    
    //unsupervised pre training
    Network network = unsupervisedPreTrainingMultipleLayers(data.inputs(), layer, numberOfClasses(data),
                                                            unsupRegularisation, noiseStrength, unsupIterations);
    
    //create the supervised problem. Cross Entropy loss with one norm regularisation
    CrossEntropy loss;
    ErrorFunction error(data, &network, &loss);
    OneNormRegularizer regularizer(error.numberOfVariables());
    error.setRegularizer(regularisation,&regularizer);
    
    //optimize the model
    std::cout<<"training supervised model"<<std::endl;
    IRpropPlusFull optimizer;
    optimizer.init(error);
    for(size_t i = 0; i != iterations; ++i){
        optimizer.step(error);
        cout<<i<<" "<<optimizer.solution().value<<std::endl;
    }
    network.setParameterVector(optimizer.solution().point);
    //###end<supervised_training>
    
    //evaluation
    ZeroOneLoss<unsigned int,RealVector> loss01;
    Data<RealVector> predictionTrain = network(data.inputs());
    cout << "classification error,train: " << loss01.eval(data.labels(), predictionTrain) << endl;
    
    Data<RealVector> prediction = network(test.inputs());
    cout << "classification error,test: " << loss01.eval(test.labels(), prediction) << endl;
    
    //output results
    exportCSV(data.inputs(), "inputs.csv");
    exportCSV(predictionTrain, "predictionTrain.csv");
    exportCSV(prediction, "prediction.csv");
}

"""ML workflow using demystifying."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from demystifying import feature_extraction as fe, visualization
from demystifying import relevance_propagation as relprop

# from sklearn.utils import shuffle
import logging

logger = logging.getLogger("Trp")


def create_combined_csv():
    """
    Generate a starting dataframe and stor in at a CSV
    """

    averaging_frame = 10.0
    # Read in original files as a dataframe
    df_1l2y = pd.read_table("1l2y-charges.xls")
    df_2jof = pd.read_table("2jof-charges.xls")
    # Atoms numbers that you would like to drop indexed at 0
    atoms_1l2y = [x for x in range(76)]
    atoms_2jof = [x for x in range(56)]
    print("\nCombining datasets.")

    # 1L2Y remove the features of the atoms that were change due to the mutation
    df_1l2y = df_1l2y.drop(df_1l2y.columns[atoms_1l2y], axis=1)
    df_1l2y = df_1l2y.iloc[:, :-1]  # The last column "Unnamed" is empty
    df_1l2y.columns = [x + 1 for x in range(len(df_1l2y.columns))]
    df_1l2y = df_1l2y.groupby(df_1l2y.index // averaging_frame).mean()

    # 2JOF remove the features of the atoms that were change due to the mutation
    df_2jof = df_2jof.drop(df_2jof.columns[atoms_2jof], axis=1)
    df_2jof = df_2jof.iloc[:, :-1]  # The last column "Unnamed" is empty
    df_2jof.columns = [x + 1 for x in range(len(df_2jof.columns))]
    df_2jof = df_2jof.groupby(df_2jof.index // averaging_frame).mean()

    # Create an array containing the labels for each frame
    print("\nCreating labels.")
    labels_1l2y = [0 for x in range(len(df_1l2y.index))]
    labels_2jof = [1 for x in range(len(df_2jof.index))]
    labels = np.array(labels_1l2y + labels_2jof)

    # Combine both dataframes into a single dataframe
    combined_df = pd.concat([df_1l2y, df_2jof], ignore_index=True, sort=False)
    # Write the data out to a new file

    return combined_df, labels


def data_processing(df, labels):
    """
    Format the data for the ML workflows
    """

    # Scale each column such that all values are between 0 and 1
    scaler = MinMaxScaler()
    df_norm = pd.DataFrame(
        scaler.fit_transform(df.values), columns=df.columns, index=df.index
    )
    # Convert it to a matrix which will leave out the row and column headers
    samples = df_norm.to_numpy()
    print("\nGenerating and scaling data.")

    # Shuffle the data in groups of 100
    n_samples = samples.shape[0]
    n_samples = int(n_samples / 100) * 100
    inds = np.arange(n_samples)
    inds = inds.reshape((int(n_samples / 100), 100))
    perm_inds = np.random.permutation(inds)
    perm_inds = np.ravel(perm_inds)
    samples = samples[perm_inds]  # Apply the shuffling to the matrix
    labels = labels[perm_inds]  # Apply the same shuffling to the labels
    print("\nShuffling data.")
    # samples, labels = shuffle(samples, labels, random_state=0)

    return samples, labels


def run_trp_cage():
    """
    Run the ML processes
    """

    # Get the processed data as a numpy array and the labels
    df, labels = create_combined_csv()
    samples, labels = data_processing(df, labels)
    np.savetxt("foo.csv", samples, delimiter=",")  # Check final matrix

    # Set the arguments for the ML workflows
    kwargs = {
        "samples": samples,
        "labels": labels,
        "filter_by_distance_cutoff": False,
        "lower_bound_distance_cutoff": 1.0,
        "upper_bound_distance_cutoff": 1.0,
        "use_inverse_distances": False,
        "n_splits": 3,
        "n_iterations": 5,
        "scaling": True,
    }

    # Running various ML workflows
    models = ["PCA", "RBM", "AE", "RF", "KL", "MLP"]
    feature_extractors = [
        fe.PCAFeatureExtractor(**kwargs),
        fe.RbmFeatureExtractor(relevance_method="from_components", **kwargs),
        fe.MlpAeFeatureExtractor(
            activation=relprop.relu,
            classifier_kwargs={"solver": "adam", "hidden_layer_sizes": (100,)},
            **kwargs,
        ),
        fe.RandomForestFeatureExtractor(
            one_vs_rest=True, classifier_kwargs={"n_estimators": 100}, **kwargs
        ),
        fe.KLFeatureExtractor(**kwargs),
        fe.MlpFeatureExtractor(
            classifier_kwargs={
                "hidden_layer_sizes": (120,),
                "solver": "adam",
                "max_iter": 1000000,
            },
            activation=relprop.relu,
            **kwargs,
        ),
    ]

    # Process the results
    postprocessors = []
    working_dir = "."
    for extractor, model in zip(feature_extractors, models):
        print(f"\nRunning {model} model.")
        extractor.extract_features()
        # Post-process data (rescale and filter feature importances)
        postprocessor = extractor.postprocessing(
            working_dir=working_dir,
            rescale_results=True,
            filter_results=False,
            feature_to_resids=None,
        )
        postprocessor.average()
        postprocessor.persist()
        postprocessors.append(postprocessor)

    # Create a summarizing plot of the results of the ML models
    visualization.visualize(
        [postprocessors],
        show_importance=True,
        show_projected_data=False,
        show_performance=False,
        highlighted_residues=[22],
        outfile="./importance.pdf",
    )


# Execute the script
if __name__ == "__main__":
    run_trp_cage()

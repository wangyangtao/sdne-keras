
# coding: utf-8

# In[47]:


import networkx as nx
import os
import tensorflow as tf
import pickle as pkl
import math
import numpy as np
import pandas as pd

from core import SDNE
from tensorflow.contrib.tensorboard.plugins import projector


# In[2]:


g = nx.read_gpickle('data/datascience.graph.pkl')


# In[83]:


model = SDNE(g, encode_dim=48, encoding_layer_dims=[100, 32],
             beta=2,
             alpha=2,
             l2_param=1e-3)


# In[89]:


batch_size = 32
n_batches = math.ceil(g.number_of_edges() / batch_size)
model.fit(epochs=100, log=True, batch_size=batch_size,
          steps_per_epoch=n_batches)


# In[90]:


embedding_values = model.encoder.predict(np.arange(g.number_of_nodes())[:, None])
embedding_var = tf.Variable(embedding_values, name='node_embeddings')


# In[101]:


embedding_values.shape


# In[99]:


emb_df = pd.DataFrame(embedding_values)
emb_df.to_csv('embeddings/stackexchange-datascience/embedding.tsv', sep='\t', header=False, index=False)


# In[91]:


LOG_DIR = 'log/stackexchange-datascience'


# In[92]:


labels = pkl.load(open('data/datascience.meta.pkl', 'rb'))
id2label = dict(zip(labels.values(), labels.keys()))
col = []
for i in range(len(labels)):
    col.append(id2label[i])
df = pd.Series(col, name='label')
df.to_frame().to_csv(LOG_DIR + '/node_labels.tsv', index=False, header=False)


# In[93]:


with tf.Session() as sess:
    saver = tf.train.Saver([embedding_var])

    sess.run(embedding_var.initializer)
    saver.save(sess, os.path.join(LOG_DIR, 'embeddings.ckpt'))
    
    config = projector.ProjectorConfig()
    # One can add multiple embeddings.
    embedding = config.embeddings.add()
    embedding.tensor_name = embedding_var.name
    # Link this tensor to its metadata file (e.g. labels).
    embedding.metadata_path = os.path.join(LOG_DIR, 'node_labels.tsv')
    # Saves a config file that TensorBoard will read during startup.
    
    projector.visualize_embeddings(tf.summary.FileWriter(LOG_DIR), config)

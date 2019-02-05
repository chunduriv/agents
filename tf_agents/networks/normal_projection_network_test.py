# coding=utf-8
# Copyright 2018 The TF-Agents Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for tf_agents.networks.normal_projection_network."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import tensorflow_probability as tfp

from tf_agents.networks import normal_projection_network
from tf_agents.specs import tensor_spec


def _get_inputs(batch_size, num_input_dims):
  return tf.random.uniform([batch_size, num_input_dims])


class NormalProjectionNetworkTest(tf.test.TestCase):

  def testBuild(self):
    output_spec = tensor_spec.BoundedTensorSpec([2], tf.float32, 0, 1)
    network = normal_projection_network.NormalProjectionNetwork(output_spec)

    inputs = _get_inputs(batch_size=3, num_input_dims=5)

    distribution = network(inputs, outer_rank=1)
    self.evaluate(tf.compat.v1.global_variables_initializer())
    self.assertEqual(tfp.distributions.Normal, type(distribution))

    means, stds = distribution.loc, distribution.scale

    self.assertAllEqual(means.shape.as_list(),
                        [3] + output_spec.shape.as_list())
    self.assertAllEqual(stds.shape.as_list(), [3] + output_spec.shape.as_list())

  def testBuildStateDepStddev(self):
    output_spec = tensor_spec.BoundedTensorSpec([2], tf.float32, 0, 1)
    network = normal_projection_network.NormalProjectionNetwork(
        output_spec, state_dependent_std=True)

    inputs = _get_inputs(batch_size=3, num_input_dims=5)

    distribution = network(inputs, outer_rank=1)
    self.evaluate(tf.compat.v1.global_variables_initializer())
    self.assertEqual(tfp.distributions.Normal, type(distribution))

    means, stds = distribution.loc, distribution.scale

    self.assertAllEqual(means.shape.as_list(),
                        [3] + output_spec.shape.as_list())
    self.assertAllEqual(stds.shape.as_list(), [3] + output_spec.shape.as_list())

  def testTrainableVariables(self):
    output_spec = tensor_spec.BoundedTensorSpec([2], tf.float32, 0, 1)
    network = normal_projection_network.NormalProjectionNetwork(output_spec)

    inputs = _get_inputs(batch_size=3, num_input_dims=5)

    network(inputs, outer_rank=1)
    self.evaluate(tf.compat.v1.global_variables_initializer())

    # Dense kernel, dense bias, std bias.
    self.assertEqual(3, len(network.trainable_variables))
    self.assertEqual((5, 2), network.trainable_variables[0].shape)
    self.assertEqual((2,), network.trainable_variables[1].shape)
    self.assertEqual((2,), network.trainable_variables[2].shape)

  def testTrainableVariablesStateDepStddev(self):
    output_spec = tensor_spec.BoundedTensorSpec([2], tf.float32, 0, 1)
    network = normal_projection_network.NormalProjectionNetwork(
        output_spec, state_dependent_std=True)

    inputs = _get_inputs(batch_size=3, num_input_dims=5)

    network(inputs, outer_rank=1)
    self.evaluate(tf.compat.v1.global_variables_initializer())

    # Dense kernel, dense bias, std bias.
    self.assertEqual(4, len(network.trainable_variables))
    self.assertEqual((5, 2), network.trainable_variables[0].shape)
    self.assertEqual((2,), network.trainable_variables[1].shape)
    self.assertEqual((5, 2), network.trainable_variables[2].shape)
    self.assertEqual((2,), network.trainable_variables[3].shape)


if __name__ == '__main__':
  tf.test.main()

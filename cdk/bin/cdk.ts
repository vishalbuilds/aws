#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { RemovePiiS3Stack } from '../lib/remove-pii-s3-stack';
import { GetTableDataStack } from '../lib/get-table-data-stack';

const app = new cdk.App();
new RemovePiiS3Stack(app, 'RemovePiiS3Stack', {
  /* env options here if needed */
});
new GetTableDataStack(app, 'GetTableDataStack', {
  /* env options here if needed */
});
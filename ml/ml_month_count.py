import os
import pandas as pd
import numpy as np
from sklearn.linear_model import ElasticNet

class DataLoader:
    def __init__(self, train_path, test_path, sample_submission_path):
        self.train_path = train_path
        self.test_path = test_path
        self.sample_submission_path = sample_submission_path

    def load_data(self):
        train = pd.read_csv(self.train_path)
        test = pd.read_csv(self.test_path)
        sample_submission = pd.read_csv(self.sample_submission_path)
        return train, test, sample_submission

class DataPreprocessor:
    def __init__(self, train):
        self.train = train

    def preprocess(self):
        self.train['date'] = pd.to_datetime(self.train['date'], format='%d.%m.%Y')
        self.train['month'] = self.train['date'].dt.month
        self.train['year'] = self.train['date'].dt.year
        self.train['day'] = self.train['date'].dt.day
        return self.train

    def aggregate_monthly_sales(self):
        monthly_sales = self.train.groupby(['date_block_num', 'shop_id', 'item_id']).agg({
            'item_cnt_day': 'sum',
            'item_price': 'mean',
        }).reset_index()
        monthly_sales.rename(columns={'item_cnt_day': 'item_cnt_month'}, inplace=True)
        monthly_sales['month'] = monthly_sales['date_block_num'] % 12
        monthly_sales['year'] = monthly_sales['date_block_num'] // 12
        return monthly_sales

class FeatureEngineer:
    @staticmethod
    def add_lag_features(df, lags, col):
        tmp = df[['date_block_num', 'shop_id', 'item_id', col]]
        for i in lags:
            shifted = tmp.copy()
            shifted.columns = ['date_block_num', 'shop_id', 'item_id', f'{col}_lag_{i}']
            shifted['date_block_num'] += i
            df = pd.merge(df, shifted, on=['date_block_num', 'shop_id', 'item_id'], how='left')
        df.fillna(0, inplace=True)
        return df

    @staticmethod
    def sample_data(monthly_sales, records_per_block, desired_total_records):
        sampled_data = pd.DataFrame()
        for block_num in range(34):
            block_data = monthly_sales[monthly_sales['date_block_num'] == block_num]
            if len(block_data) > records_per_block:
                sampled_data = pd.concat([sampled_data, block_data.sample(n=records_per_block, random_state=42)])
            else:
                sampled_data = pd.concat([sampled_data, block_data])

        sampled_data.reset_index(drop=True, inplace=True)
        if len(sampled_data) > desired_total_records:
            sampled_data = sampled_data.sample(n=desired_total_records, random_state=42)
        return sampled_data

class SubmissionMaker:
    @staticmethod
    def prepare_test_set(test, sampled_data, lags, features):
        test['month'] = 34 % 12
        test['year'] = 34 // 12
        test = pd.merge(test, sampled_data[['shop_id', 'item_id', 'item_price']], on=['shop_id', 'item_id'], how='left')

        for lag in lags:
            lag_col_name = f'item_cnt_month_lag_{lag}'
            lag_data = sampled_data[sampled_data['date_block_num'] == (34 - lag)][['shop_id', 'item_id', 'item_cnt_month']]
            lag_data.columns = ['shop_id', 'item_id', lag_col_name]
            test = pd.merge(test, lag_data, on=['shop_id', 'item_id'], how='left')

        test.fillna(0, inplace=True)
        for feature in features:
            if feature not in test.columns:
                test[feature] = 0

        # Drop columns that are not part of the features
        test = test[features]
        return test

    @staticmethod
    def create_submission(model, X_test, sample_submission):
        sample_submission['item_cnt_month'] = model.predict(X_test)
        sample_submission.to_csv("month_revenue.csv", index=False)

def main():
    # Load data
    data_loader = DataLoader(
        train_path="../database/sales_train.csv",
        test_path="../database/test.csv",
        sample_submission_path="../database/sample_submission.csv"
    )
    train, test, sample_submission = data_loader.load_data()

    # Preprocess data
    preprocessor = DataPreprocessor(train)
    train = preprocessor.preprocess()
    monthly_sales = preprocessor.aggregate_monthly_sales()

    # Feature engineering
    monthly_sales = FeatureEngineer.add_lag_features(monthly_sales, [1, 2, 3], 'item_cnt_month')
    sampled_data = FeatureEngineer.sample_data(monthly_sales, records_per_block=10000, desired_total_records=330000)

    # Split data
    features = ['shop_id', 'item_id', 'item_price', 'month', 'year',
                'item_cnt_month_lag_1', 'item_cnt_month_lag_2', 'item_cnt_month_lag_3']
    target = 'item_cnt_month'

    X_train = sampled_data[sampled_data['date_block_num'] < 33][features]
    y_train = sampled_data[sampled_data['date_block_num'] < 33][target]

    # Train model
    model = ElasticNet(random_state=1, alpha=1.0, l1_ratio=1.0)
    model.fit(X_train, y_train)

    # Prepare test set and create submission
    X_test = SubmissionMaker.prepare_test_set(test, sampled_data, lags=[1, 2, 3], features=features)
    X_test = X_test[:214200]  # Limit to a specific size if necessary

    SubmissionMaker.create_submission(model, X_test, sample_submission)

if __name__ == "__main__":
    main()

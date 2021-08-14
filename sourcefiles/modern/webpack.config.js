const webpack = require('webpack');
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const paths = {
  plugin: '../../plugin/',
  public: '../../plugin/public/modern/js/',
  tmpl: '../../plugin/controllers/views/responsive/',
};

const config = {
  // context: path.resolve(__dirname, 'app'),
  entry: {
    owif:          ['./entry-app'],
    autotimers:    ['./autotimers-app'],
    bouqueteditor: ['./bqe-app'],
  },
  output: {
    path: path.resolve(__dirname, `${paths['public']}`),
    filename: '[name]-app.[contenthash].js',
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        use: 'babel-loader',
        exclude: /node_modules/
      }
    ]
  },
  plugins: [
    // //for future use (1)
    // new webpack.ProvidePlugin({
    //     $: 'jquery',
    // }),
    new HtmlWebpackPlugin({
      // appMountId: 'fullmaincontent',
      template: './tmpl/main.tmpl',
      filename: path.resolve(__dirname, `${paths['tmpl']}main.tmpl`),
      chunks: ['owif'],
      publicPath: paths['public'],
      scriptLoading: 'blocking',
      inject: false,
      minify: false,
    }),
    new HtmlWebpackPlugin({
      // appMountId: 'content_main',
      template: './tmpl/at.tmpl',
      filename: path.resolve(__dirname, `${paths['tmpl']}ajax/at.tmpl`),
      chunks: ['autotimers'],
      publicPath: paths['public'],
      scriptLoading: 'blocking',
      inject: false,
      minify: false,
    }),
    new HtmlWebpackPlugin({
      // appMountId: 'bqemain',
      template: './tmpl/bqe.tmpl',
      filename: path.resolve(__dirname, `${paths['tmpl']}ajax/bqe.tmpl`),
      chunks: ['bouqueteditor'],
      publicPath: paths['public'],
      scriptLoading: 'blocking',
      inject: false,
      minify: false,
    }),
  ],
  // for future use (2)
  // optimization: {
  //   runtimeChunk: 'single',
  //   splitChunks: {
  //     cacheGroups: {
  //       vendor: {
  //         test: /[\\/]node_modules[\\/]/,
  //         name: 'vendors',
  //         chunks: 'all'
  //       }
  //     }
  //   }
  // }
};

module.exports = config;

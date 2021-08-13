const webpack = require('webpack');
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const publicPath = '/modern/js/';

const config = {
  entry: {
    owif:          ['./entry-app.js'],
    autotimers:    ['./autotimers-app.js'],
    bouqueteditor: ['./bqe-app.js'],
  },
  output: {
    path: path.resolve(__dirname, '../../plugin/public' + publicPath),
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
      filename: './tmpl/main.tmpl',
      template: '../../plugin/controllers/views/responsive/main.tmpl',
      chunks: ['owif'],
      publicPath: publicPath,
      inject: false,
      scriptLoading: 'blocking',
      minify: false,
    }),
    new HtmlWebpackPlugin({
      // appMountId: 'content_main',
      filename: './tmpl/at.tmpl',
      template: '../../plugin/controllers/views/responsive/ajax/at.tmpl',
      chunks: ['autotimers'],
      publicPath: publicPath,
      inject: false,
      scriptLoading: 'blocking',
      minify: false,
    }),
    new HtmlWebpackPlugin({
      // appMountId: 'bqemain',
      filename: './tmpl/bqe.tmpl',
      template: '../../plugin/controllers/views/responsive/ajax/bqe.tmpl',
      chunks: ['bouqueteditor'],
      publicPath: publicPath,
      inject: false,
      scriptLoading: 'blocking',
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

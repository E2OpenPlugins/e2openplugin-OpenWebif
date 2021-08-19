const webpack = require('webpack');
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const paths = {
  plugin: '../../plugin/',
  public: '/modern/js/',
  tmpl:   '../../plugin/controllers/views/responsive/',
};

const config = {
  // context: path.resolve(__dirname, 'app'),
  entry: {
    owif:          './entry-app',
    autotimers:    './autotimers-app',
    bouqueteditor: './bqe-app',
  },
  output: {
    path: path.resolve(__dirname, `${paths['plugin']}public${paths['public']}`),
    publicPath: paths['public'],
    filename: '[name]-app.js',
    // // for future use (asset versioning)
    // filename: '[name]-app.[contenthash].js',
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
    // for future use (asset versioning)
    // new HtmlWebpackPlugin({
    //   // appMountId: 'fullmaincontent',
    //   template: './tmpl/main.tmpl',
    //   filename: path.resolve(__dirname, `${paths['tmpl']}main.tmpl`),
    //   minify: false,
    //   chunks: ['owif'],
    //   scriptLoading: 'blocking',
    //   inject: false,
    // }),
    // new HtmlWebpackPlugin({
    //   // appMountId: 'content_main',
    //   template: './tmpl/at.tmpl',
    //   filename: path.resolve(__dirname, `${paths['tmpl']}ajax/at.tmpl`),
    //   minify: false,
    //   chunks: ['autotimers'],
    //   scriptLoading: 'blocking',
    //   inject: false,
    // }),
    // new HtmlWebpackPlugin({
    //   // appMountId: 'bqemain',
    //   template: './tmpl/bqe.tmpl',
    //   filename: path.resolve(__dirname, `${paths['tmpl']}ajax/bqe.tmpl`),
    //   minify: false,
    //   chunks: ['bouqueteditor'],
    //   scriptLoading: 'blocking',
    //   inject: false,
    // }),
  ],
  optimization: {
    emitOnErrors: true,
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
    runtimeChunk: { 
      name: 'runtime',
    },
  },
};

module.exports = (env, argv) => {
  if (argv.mode === 'development') {
    config.output.filename = '[name]-app.js';
    config.output.clean = false;
  }

  return config;
};

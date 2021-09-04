const webpack = require('webpack');
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const paths = {
  public: '/modern/js/',
  plugin: '../../plugin/',
  tmpl:   '../../plugin/controllers/views/responsive/',
};

const legacyJsFiles = [
  path.resolve(__dirname, 'js', 'openwebif.js'),
  path.resolve(__dirname, 'js', 'vti-responsive-epgr.js'),
  path.resolve(__dirname, 'js', 'vti-responsive-multiepg.js'),
  path.resolve(__dirname, 'js', 'vti-bootstrap-date-timepicker.js'),
  path.resolve(__dirname, 'js', 'admin.js'),
  path.resolve(__dirname, 'js', 'vti-responsive.js'),
  path.resolve(__dirname, 'js', 'vti.js'),
];

const config = {
  // context: path.resolve(__dirname, 'app'),
  entry: {
    owif:          './entry-app',
    autotimers:    './autotimers-app',
    bouqueteditor: './bqe-app',
    legacy:        legacyJsFiles,
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
        type: 'asset/resource',
        generator: {
          filename: '[name].min[ext]',
          // // for future use (asset versioning)
          // filename: '[name].min.[contenthash][ext]',
        },
        include: legacyJsFiles,
      },
      {
        test: /\.js$/,
        use: 'babel-loader',
        exclude: [
          /[\\/]node_modules[\\/]/,
          /[\\/]plugins[\\/]/,
        ].concat(legacyJsFiles),
      },
    ],
  },
  externals: {
    // require("jquery") is external and available on the global var jQuery
    "jquery": "jQuery"
  },
  plugins: [
    // for future use (asset versioning)
    // new HtmlWebpackPlugin({
    //   // appMountId: 'fullmaincontent',
    //   template: './tmpl/main.tmpl',
    //   filename: path.resolve(__dirname, `${paths['tmpl']}main.tmpl`),
    //   minify: false,
    //   chunks: ['owif', 'legacy'],
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
  },
};

module.exports = (env, argv) => {
  if (argv.mode === 'development') {
    config.output.filename = '[name]-app.js';
    config.output.clean = false;
  }

  return config;
};

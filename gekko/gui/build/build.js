'use strict'
require('./check-versions')()

process.env.NODE_ENV = 'production'

const ora = require('ora')
const rm = require('rimraf')
const path = require('path')
const chalk = require('chalk')
const webpack = require('webpack')
const config = require('../config')
const webpackConfig = require('./webpack.prod.conf')
const fs = require('fs')

const spinner = ora('building for production...')
spinner.start()

function copyFileSync( source, target ) {

    var targetFile = target;

    //if target is a directory a new file with the same name will be created
    if ( fs.existsSync( target ) ) {
        if ( fs.lstatSync( target ).isDirectory() ) {
            targetFile = path.join( target, path.basename( source ) );
        }
    }

    fs.writeFileSync(targetFile, fs.readFileSync(source));
}

function copyFolderRecursiveSync( source, target ) {
    var files = [];

    //check if folder needs to be created or integrated
    var targetFolder = path.join( target, path.basename( source ) );
    if ( !fs.existsSync( targetFolder ) ) {
        fs.mkdirSync( targetFolder );
    }

    //copy
    if ( fs.lstatSync( source ).isDirectory() ) {
        files = fs.readdirSync( source );
        files.forEach( function ( file ) {
            var curSource = path.join( source, file );
            if ( fs.lstatSync( curSource ).isDirectory() ) {
                copyFolderRecursiveSync( curSource, targetFolder );
            } else {
                copyFileSync( curSource, targetFolder );
            }
        } );
    }
}

rm(path.join(config.build.assetsRoot, config.build.assetsSubDirectory), err => {
  if (err) throw err
  webpack(webpackConfig, (err, stats) => {
    spinner.stop()
    if (err) throw err
    process.stdout.write(stats.toString({
      colors: true,
      modules: false,
      children: false, // If you are using ts-loader, setting this to true will make TypeScript errors show up during build.
      chunks: false,
      chunkModules: false
    }) + '\n\n')

    if (stats.hasErrors()) {
      console.log(chalk.red('  Build failed with errors.\n'))
      process.exit(1)
    }

    console.log(chalk.cyan('  Build complete.\n'))
    console.log(chalk.yellow(
      '  Tip: built files are meant to be served over an HTTP server.\n' +
      '  Opening index.html over file:// won\'t work.\n'
    ))
    // File copy actually goes here
    console.log('Copying built files to GEKKO static folder...')
    // Replace the files in gekko/static with the built files from gekko/gui/dist
    const srcDir = path.join(__dirname, '..', 'dist')
    const destDir = path.join(__dirname, '..', '..', 'static')
    if (fs.existsSync(destDir)) {
      rm.sync(destDir)
    }
    fs.mkdirSync(destDir)
    const builtFiles = fs.readdirSync(srcDir)
    for (var i = 0; i < builtFiles.length; i++) {
      // We only need to worry about one layer deep right now, so no recursion necessary
      if (fs.statSync(path.join(srcDir, builtFiles[i])).isDirectory()) {
        copyFolderRecursiveSync(path.join(srcDir, builtFiles[i]), destDir)
      } else {
        fs.copyFileSync(path.join(srcDir, builtFiles[i]), path.join(destDir, builtFiles[i]))
      }
    }
    console.log('Copy complete.\n')
  })
})

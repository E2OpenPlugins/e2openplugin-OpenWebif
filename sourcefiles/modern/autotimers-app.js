//******************************************************************************
//* at.js: openwebif AutoTimer plugin
//* Version 3.0
//******************************************************************************
//* Authors: Web Dev Ben <https://github.com/wedebe>
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************

// for future use (read autotimer.xml into json)
// https://www.npmjs.com/package/xml2json-light-es6module
// function xml2json(xmlStr){return xml2jsonRecurse(xmlStr=cleanXML(xmlStr),0)} function xml2jsonRecurse(xmlStr){for(var obj={},tagName,indexClosingTag,inner_substring,tempVal,openingTag;xmlStr.match(/<[^\/][^>]*>/);)tagName=(openingTag=xmlStr.match(/<[^\/][^>]*>/)[0]).substring(1,openingTag.length-1),-1==(indexClosingTag=xmlStr.indexOf(openingTag.replace("<","</")))&&(tagName=openingTag.match(/[^<][\w+$]*/)[0],-1==(indexClosingTag=xmlStr.indexOf("</"+tagName))&&(indexClosingTag=xmlStr.indexOf("<\\/"+tagName))),tempVal=(inner_substring=xmlStr.substring(openingTag.length,indexClosingTag)).match(/<[^\/][^>]*>/)?xml2json(inner_substring):inner_substring,void 0===obj[tagName]?obj[tagName]=tempVal:Array.isArray(obj[tagName])?obj[tagName].push(tempVal):obj[tagName]=[obj[tagName],tempVal],xmlStr=xmlStr.substring(2*openingTag.length+1+inner_substring.length);return obj} function cleanXML(xmlStr){return xmlStr=replaceAttributes(xmlStr=replaceAloneValues(xmlStr=replaceSelfClosingTags(xmlStr=(xmlStr=(xmlStr=(xmlStr=(xmlStr=xmlStr.replace(/<!--[\s\S]*?-->/g,"")).replace(/\n|\t|\r/g,"")).replace(/ {1,}<|\t{1,}</g,"<")).replace(/> {1,}|>\t{1,}/g,">")).replace(/<\?[^>]*\?>/g,""))))} function replaceSelfClosingTags(xmlStr){var selfClosingTags=xmlStr.match(/<[^/][^>]*\/>/g);if(selfClosingTags)for(var i=0;i<selfClosingTags.length;i++){var oldTag=selfClosingTags[i],tempTag=oldTag.substring(0,oldTag.length-2);tempTag+=">";var tagName=oldTag.match(/[^<][\w+$]*/)[0],closingTag="</"+tagName+">",newTag="<"+tagName+">",attrs=tempTag.match(/(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?/g);if(attrs)for(var j=0;j<attrs.length;j++){var attr=attrs[j],attrName=attr.substring(0,attr.indexOf("=")),attrValue;newTag+="<"+attrName+">"+attr.substring(attr.indexOf('"')+1,attr.lastIndexOf('"'))+"</"+attrName+">"}newTag+=closingTag,xmlStr=xmlStr.replace(oldTag,newTag)}return xmlStr} function replaceAloneValues(xmlStr){var tagsWithAttributesAndValue=xmlStr.match(/<[^\/][^>][^<]+\s+.[^<]+[=][^<]+>{1}([^<]+)/g);if(tagsWithAttributesAndValue)for(var i=0;i<tagsWithAttributesAndValue.length;i++){var oldTag=tagsWithAttributesAndValue[i],oldTagName,oldTagValue,newTag=oldTag.substring(0,oldTag.indexOf(">")+1)+"<_@ttribute>"+oldTag.substring(oldTag.indexOf(">")+1)+"</_@ttribute>";xmlStr=xmlStr.replace(oldTag,newTag)}return xmlStr} function replaceAttributes(xmlStr){var tagsWithAttributes=xmlStr.match(/<[^\/][^>][^<]+\s+.[^<]+[=][^<]+>/g);if(tagsWithAttributes)for(var i=0;i<tagsWithAttributes.length;i++){var oldTag=tagsWithAttributes[i],tagName,newTag="<"+oldTag.match(/[^<][\w+$]*/)[0]+">",attrs=oldTag.match(/(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?/g);if(attrs)for(var j=0;j<attrs.length;j++){var attr=attrs[j],attrName=attr.substring(0,attr.indexOf("=")),attrValue;newTag+="<"+attrName+">"+attr.substring(attr.indexOf('"')+1,attr.lastIndexOf('"'))+"</"+attrName+">"}xmlStr=xmlStr.replace(oldTag,newTag)}return xmlStr}

(function () {
  const regexDateFormat = new RegExp(/\d{4}-\d{2}-\d{2}/);

  const apiRequest = async (url, method = 'get', payload) => {
    try {
      const response = await fetch(url, {
        method: method,
        body: payload, //new URLSearchParams([...payload]),
      });

      if (response.ok) {
        return response;
      } else {
        throw new Error(response.statusText || response.status);
      }
    } catch (ex) {
      throw new Error(ex);
    }
  };

  const AutoTimers = function () {
    const atForm = document.getElementById('atform');

    const addDependentSectionTogglers = (data = {Tags:[], Channels: [], Bouquets: [], ...{}}) => {
        // set up show/hide checkboxes
        data['_timespan'] = !!data.timespanFrom || !!data.timespanTo;
        data['_after'] = !!data.after;
        data['_before'] = !!data.before;
        data['_timerOffset'] = !!data.timerOffsetAfter || !!data.timerOffsetBefore;
        data['_location'] = !!data.location;
        data['_tags'] = !!data.Tags.length;
        data['_channels'] = !!data.Channels.length;
        data['_bouquets'] = !!data.Bouquets.length;

        return data;
      };

    return {
      populateForm: (data) => {
        const allChannels = autoTimerOptions['channels']['_currentState']['choices'];
        const allBouquets = autoTimerOptions['bouquets']['_currentState']['choices'];

        const { elements } = atForm;
        atForm.reset();

        data = addDependentSectionTogglers(data);

        for (const [key, value] of Object.entries(data)) {
          let field = elements.namedItem(key);
          if (field) {
            console.log(`[${field.type}]`, key, value);
            switch (field.type) {
              case 'checkbox':
                field.checked = value;
                break;
              default:
                field.value = value;
                break;
            }
            field.dispatchEvent(new Event('change'));
          } else {
            console.log('%c[N/A]', 'color: red', key, value);
          }
        }
        var tagOpts = [];
        try {
          tagOpts = window.tagList.map(function (item) {
            let allTags = autoTimerOptions['tags']['_currentState']['choices'];
            let isFound = false;
            allTags.forEach(function (tg) {
              if (item === tg.value) {
                isFound = true;
              }
            });
            return (isFound) ? false : {
              value: item,
              label: item,
            }
          });
          tagOpts.push(data.Tags);
        } catch(e) {
          console.debug('Failed to process tag options');
        }

        autoTimerOptions['tags']
          .setChoices(tagOpts, 'value', 'label', false)
          .removeActiveItems()
          .setChoiceByValue(data.Tags);
      
        autoTimerOptions['channels']
          .setChoices(allChannels, 'value', 'label', false)
          .removeActiveItems()
          .setChoiceByValue(data.Channels);
      
        autoTimerOptions['bouquets']
          .setChoices(allBouquets, 'value', 'label', false)
          .removeActiveItems()
          .setChoiceByValue(data.Bouquets);
      },

      // .then(response => response.formData())

      saveEntry: (extraParams = '') => {
        const formData = new FormData(atForm);
        const formDataObj = Object.fromEntries(formData);

        Object.entries(formDataObj).forEach(([name, value]) => {
          console.log(name, value);
          if (name === 'id' && value === '') {
            // remove empty value (empty id causes server error, but missing id does not)
            formData.delete(name);
          } else if (regexDateFormat.test(value)) {
            // convert html date input format (yyyy-mm-dd) to serial
            formData.set(name, Date.parse(`${value}Z`) / 1000); // Z is intentional
          } else if (name !== 'tag') {
            // join multiple param= values into an array
            formData.set(name, formData.getAll(name));
          }
        });

        apiRequest(`/autotimer/edit?${extraParams}`, 'post', formData)
          .then(response => response.text())
          .then(responseText => {
            const responseXml = new DOMParser().parseFromString(responseText, 'application/xml');
            const status = responseXml.getElementsByTagName('e2state')[0].textContent || '';
            const message = responseXml.getElementsByTagName('e2statetext')[0].textContent || '';

            if (status === true || status.toString().toLowerCase() === 'true') {
              swal({
                title: message,
                text: '',
                type: 'success',
                animation: 'none',
              });
            } else {
              throw new Error(message);
            }
          })
          .catch((ex) => {
            let message = ex.message;
            message = message.charAt(0).toUpperCase() + message.slice(1);
            swal({
              title: message,
              text: '',
              type: 'error',
              animation: 'none',
            });
          });
      },

      initEventHandlers: () => {
        // create a failsafe element to assign event handlers to
        let nullEl = document.createElement('input');

        (document.getElementById('_timespan') || nullEl).onchange = (input) => {
          document.getElementById('timeSpanE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_after') || nullEl).onchange = (input) => {
          document.getElementById('timeFrameE').classList.toggle('dependent-section', !input.target.checked);
          // document.getElementById('timeFrameAfterCheckBox').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_before') || nullEl).onchange = (input) => {
          document.getElementById('beforeE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_timerOffset') || nullEl).onchange = (input) => {
          document.getElementById('timerOffsetE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('timeSpanAE') || nullEl).onchange = (input) => {
          document.getElementById('timeSpanAEE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_location') || nullEl).onchange = (input) => {
          document.getElementById('LocationE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_tags') || nullEl).onchange = (input) => {
          document.getElementById('TagsE').classList.toggle('dependent-section', !input.target.checked);
          // if (!input.target.checked) {
          //   try {
          //     autoTimerOptions['tags'].removeActiveItems();
          //   } catch(e){}
          // }
        };
        (document.getElementById('_bouquets') || nullEl).onchange = (input) => {
          document.getElementById('BouquetsE').classList.toggle('dependent-section', !input.target.checked);
          // if (!input.target.checked) {
          //   try {
          //     autoTimerOptions['bouquets'].removeActiveItems();
          //   } catch(e){}
          // }
        };
        (document.getElementById('_channels') || nullEl).onchange = (input) => {
          document.getElementById('ChannelsE').classList.toggle('dependent-section', !input.target.checked);
          // if (!input.target.checked) {
          //   try {
          //     autoTimerOptions['channels'].removeActiveItems();
          //   } catch(e){}
          // }
        };
        (document.getElementById('beforeevent') || nullEl).onchange = (input) => {
          document.getElementById('BeforeeventE').toggle(!!input.target.value);
        };
        (document.getElementById('afterevent') || nullEl).onchange = (input) => {
          // document.getElementById('AftereventE').toggle(!!input.target.value);
        };
        (document.getElementById('counter') || nullEl).onchange = (input) => {
          //document.getElementById('CounterE').toggle(!!input.target.value);
        };
        (document.getElementById('vps') || nullEl).onchange = (input) => {
          document.getElementById('vpsE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_filters') || nullEl).onclick = (input) => {
          $('.FilterE').toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('AddFilter') || nullEl).onclick = () => {
          AddFilter('', '', '');
        };

        nullEl = null;
      },

      init: function () {
        self = this;
        self.initEventHandlers();
      },
    };
  };

  window.autoTimers = new AutoTimers();
  window.autoTimers.init();
})();
